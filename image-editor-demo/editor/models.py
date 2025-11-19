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
    is_approved = models.BooleanField(default=False)
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