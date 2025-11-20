# editor/services/task_view_service.py
# [SVC-2] TASK-UI
# - Task + UserProfile 기준으로 템플릿 표시용 action 정보 구성

from editor.models import Task, UserProfile


def decorate_task_action_for_user(task: Task, profile: UserProfile) -> None:
    """
    TaskAssignment + Task 상태를 보고
    템플릿에서 쓸 action 정보를 task 에 붙인다.
    - task.action_is_button: 버튼 여부(bool)
    - task.action_label: 버튼/라벨 텍스트
    """
    role = profile.role
    task.action_is_button = False
    task.action_label = "-"

    # admin 은 이 섹션에서 버튼 없음
    if role == "admin":
        task.action_label = "-"
        return

    # 현재 유저의 이 Task에 대한 assignment (역할별 최신 1개만 사용)
    assignments = [a for a in task.assignments.all() if a.user_id == profile.id]

    def find_assignment(r):
        for a in assignments:
            if a.role == r:
                return a
        return None

    if role == "worker":
        ass = find_assignment("worker")
        if ass is None:
            # 아직 한 번도 신청 안 한 경우: 신청 가능 조건 체크
            if task.progress_status != "worker_done":
                task.action_is_button = True
                task.action_label = "작업 신청"
        else:
            # 이미 신청/배정 이력 있음
            if ass.status == "pending":
                task.action_label = "승인 대기"
            elif ass.status == "active":
                task.action_label = "작업 진행 중"
            elif ass.status == "finished":
                task.action_label = "작업 완료"
            elif ass.status == "rejected":
                # 거절된 경우, 다시 신청 가능하도록 할지 정책에 따라 조정
                task.action_is_button = True
                task.action_label = "다시 신청"

    elif role == "reviewer":
        ass = find_assignment("reviewer")
        if ass is None:
            # 검수 신청 가능 조건: worker_done 상태
            if task.progress_status == "worker_done":
                task.action_is_button = True
                task.action_label = "검수 신청"
        else:
            if ass.status == "pending":
                task.action_label = "승인 대기"
            elif ass.status == "active":
                task.action_label = "검수 진행 중"
            elif ass.status == "finished":
                task.action_label = "검수 완료"
            elif ass.status == "rejected":
                task.action_is_button = True
                task.action_label = "다시 신청"
