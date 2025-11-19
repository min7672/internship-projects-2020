from django.conf import settings
from django.db import models
from allauth.socialaccount.models import SocialAccount as DefaultSocialAccount

"""
User / SocialAccount / UserProfile 구조 요약

- Django User : 기본 인증 주체(PK). 소셜/일반 로그인 모두 여기 연결됨.
- SocialAccount : 소셜 로그인 계정 정보(allauth). provider + uid 로 소셜 중복 방지.
- UserProfile : 실제 서비스 회원 정보. User 와 1:1, SocialAccount 와 optional 1:1.

UserProfile 이 서비스에서 사용하는 필드(승인, 역할, 연락처 등)를 관리한다.
"""
class UserProfile(models.Model):
    # 기본 연결
    user = models.OneToOneField( settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile" ) # Django 기본 User 와 1:1 연결 (핵심 계정)
    social_account = models.OneToOneField( DefaultSocialAccount, on_delete=models.SET_NULL, null=True, blank=True, related_name="profile" )# 소셜 연결 (없으면 NULL)

    # 고유 정보 (서비스 자체 저장)
    phone_number = models.CharField(max_length=50, blank=True, default="")
    email_address = models.EmailField(max_length=254, blank=True, default="")
    
    extra_data = models.JSONField(default=dict, blank=True) # 소셜/추가 정보 JSON 저장

    # 계정 상태/역할 설정
    ROLE_CHOICES = ( ("worker", "작업자"), ("reviewer", "검수자"), ("admin", "관리자"), )
    role = models.CharField( max_length=20, choices=ROLE_CHOICES, default="worker" )

    # 메타 정보
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # 소셜 이름 → 프로필 extra → 기본 username 순으로 표시
        return (
            self.extra_data.get("name")
            if isinstance(self.extra_data, dict) and "name" in self.extra_data
            else self.user.get_username()
        )
    
class Task(models.Model):
    """
    DICOM/임상데이터 작업 단위 하나를 표현하는 테이블.
    기존 TaskList 를 대체하는 역할.
    """

    # ---- 기본 메타 정보 ----
    task_title = models.CharField(max_length=100)          # 작업 이름 (기존 task_title)
    task_request = models.CharField(max_length=100)        # 요구 작업 요약 (기존 task_request)
    description = models.TextField(blank=True)             # 상세 설명(신규, 옵션)

    # 작업 유형 (기존 CHOICES_TASK_TYPE 유지)
    TASK_TYPE_CHOICES = [ ("IM", "image_편집"), ("DT", "임상 데이터 수정"), ("DN", "DNA 데이터 수정"), ]
    task_type = models.CharField( max_length=2, choices=TASK_TYPE_CHOICES, default="IM", db_index=True, )

    # 작업 등록자
    owner = models.ForeignKey( UserProfile, on_delete=models.SET_NULL, related_name="owned_tasks", null=True, blank=True, help_text="이 작업을 생성한 사용자", )

    # ---- 보상/진행률 ----
    reward = models.PositiveIntegerField(default=0)        # 보수 금액

    # 작업 진행률(%) – 기존 필드명 유지
    pre_task = models.PositiveIntegerField(default=0)      # 작업 진행률 (예: 편집 완료율)
    ins_task_1 = models.PositiveIntegerField(default=0)    # 1차 검수 진행률
    task_rate = models.PositiveIntegerField(default=0)     # 전체 진척률(집계용)

    # ---- 데이터/이미지 경로 ----
    task_path_CT = models.CharField( max_length=255, null=True, blank=True, help_text="CT DICOM 디렉토리 경로", )
    task_path_PET = models.CharField( max_length=255, null=True, blank=True, help_text="PET DICOM 디렉토리 경로", )
    task_path_data = models.CharField( max_length=255, null=True, blank=True, help_text="임상/표 데이터 파일 경로", )

    STATUS_CHOICES = [ ("ready", "대기"), ("working", "작업중"), ("worker_done", "작업 완료"), ("review", "검수중"), ("review_done", "검수 완료"), ("archived", "보관"), ]
    progress_status  = models.CharField( max_length=20, choices=STATUS_CHOICES, default="ready", db_index=True, )

    is_active = models.BooleanField(default=True)

    # ---- 타임스탬프 ----
    created_at = models.DateTimeField(auto_now_add=True)   # 등록일자 (기존 reg_date 대체)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.get_task_type_display()}] {self.task_title}"
    
class TaskAssignment(models.Model):

    ROLE_CHOICES = [ ("worker", "작업자"), ("reviewer", "검수자"), ("owner", "등록자"), ]

    user = models.ForeignKey( UserProfile, on_delete=models.CASCADE, related_name="task_assignments", )
    task = models.ForeignKey( Task, on_delete=models.CASCADE, related_name="assignments", )
    role = models.CharField( max_length=20, choices=ROLE_CHOICES, default="worker", )

    # ---- 상태 관리 ----
    ASSIGN_STATUS = [("open", "신청 가능"), ("pending", "승인 대기"), ("assigned", "할당됨"), ("rejected", "거절됨"), ]
    status  = models.CharField( max_length=20, choices=ASSIGN_STATUS, default="open", )

    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "task", "role")  # 한 작업에 같은 역할로 중복 배정 방지
        indexes = [
            models.Index(fields=["task", "role"]),
            models.Index(fields=["user", "role"]),
        ]

    def __str__(self):
        return f"{self.user} -> {self.task} ({self.get_role_display()})"