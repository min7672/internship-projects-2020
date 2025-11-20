# editor/services/task_service.py
# [SVC-1] TASK-STATE
# - Task 상태 전환 / 권한 체크 / 도메인 예외

from dataclasses import dataclass

from editor.models import Task, UserProfile, TaskAssignment


class TaskServiceError(Exception):
    """Task 상태 전환 관련 공통 예외."""
    pass


@dataclass
class TaskServiceResult:
    """서비스 처리 결과(성공/메시지용)."""
    message: str


def apply_task(task: Task, profile: UserProfile) -> TaskServiceResult:
    """
    worker / reviewer 가 작업 또는 검수를 '신청'하는 도메인 로직.
    - worker:
        progress_status != worker_done 인 작업에 신청 가능
        → TaskAssignment(role=worker, status=pending) 생성
    - reviewer:
        progress_status == worker_done 인 작업에 검수 신청 가능
        → TaskAssignment(role=reviewer, status=pending) 생성
    - admin 은 신청 불가
    """
    role = profile.role

    if role == "admin":
        raise TaskServiceError("관리자는 작업/검수를 신청할 수 없습니다.")

    # worker 신청
    if role == "worker":
        if task.progress_status == "worker_done":
            raise TaskServiceError("이미 작업 완료 단계의 작업입니다.")

        # 이미 신청/배정 이력 있는지 확인 (거절 제외)
        exists = TaskAssignment.objects.filter(
            task=task,
            user=profile,
            role="worker",
        ).exclude(status="rejected").exists()
        if exists:
            raise TaskServiceError("이미 이 작업에 대한 신청/배정 내역이 있습니다.")

        TaskAssignment.objects.create(
            task=task,
            user=profile,
            role="worker",
            status="pending",
        )
        return TaskServiceResult(
            message=f"작업 #{task.id} 신청이 접수되었습니다. 관리자 승인 대기 중입니다."
        )

    # reviewer 신청 (검수 신청)
    if role == "reviewer":
        if task.progress_status != "worker_done":
            raise TaskServiceError("검수 신청이 가능한 작업 상태가 아닙니다.")

        exists = TaskAssignment.objects.filter(
            task=task,
            user=profile,
            role="reviewer",
        ).exclude(status="rejected").exists()
        if exists:
            raise TaskServiceError("이미 이 작업에 대한 검수 신청/배정 내역이 있습니다.")

        TaskAssignment.objects.create(
            task=task,
            user=profile,
            role="reviewer",
            status="pending",
        )
        return TaskServiceResult(
            message=f"작업 #{task.id} 검수 신청이 접수되었습니다. 관리자 승인 대기 중입니다."
        )

    raise TaskServiceError("신청 권한이 없습니다.")


def approve_task(task: Task, profile: UserProfile) -> TaskServiceResult:
    """
    admin 이 '승인 대기(pending)' 상태의 TaskAssignment 를 승인하는 도메인 로직.
    - worker pending 승인:
        TaskAssignment.status = active
        Task.progress_status 가 ready 면 working 으로 전환
    - reviewer pending 승인 (worker_done 상태에서):
        TaskAssignment.status = active
        Task.progress_status = review 로 전환
    """
    if profile.role != "admin":
        raise TaskServiceError("승인 권한이 없습니다.")

    try:
        # 단순화를 위해 한 시점에 하나의 pending 만 있다고 가정
        assignment = TaskAssignment.objects.get(task=task, status="pending")
    except TaskAssignment.DoesNotExist:
        raise TaskServiceError("승인할 신청 내역이 없습니다.")

    # 검수 승인 (작업자 완료 후, 검수자가 신청한 경우)
    if task.progress_status == "worker_done" and assignment.role == "reviewer":
        assignment.status = "active"
        assignment.save()

        task.progress_status = "review"
        task.save()

        return TaskServiceResult(
            message=f"작업 #{task.id} 검수 진행을 승인했습니다."
        )

    # 일반 작업 승인 (worker 신청)
    if assignment.role == "worker":
        assignment.status = "active"
        assignment.save()

        if task.progress_status == "ready":
            task.progress_status = "working"
            task.save()

        return TaskServiceResult(
            message=f"작업 #{task.id} 작업 진행을 승인했습니다."
        )

    raise TaskServiceError("승인할 수 없는 신청 유형입니다.")


def mark_work_done(task: Task, profile: UserProfile) -> TaskServiceResult:
    """
    worker 가 '작업 완료'를 제출하는 도메인 로직.
    - 현재 본인이 worker/active 로 배정되어 있어야 함
    - Task.progress_status == working 인 경우만 허용
    - 완료 후:
        해당 TaskAssignment.status = finished
        Task.progress_status = worker_done
        → 검수 신청 가능 상태로 전환
    """
    if profile.role != "worker":
        raise TaskServiceError("작업 완료를 제출할 권한이 없습니다.")

    try:
        assignment = TaskAssignment.objects.get(
            task=task,
            user=profile,
            role="worker",
            status="active",
        )
    except TaskAssignment.DoesNotExist:
        raise TaskServiceError("이 작업의 담당 작업자가 아닙니다.")

    if task.progress_status != "working":
        raise TaskServiceError("작업 중인 상태의 작업만 완료로 제출할 수 있습니다.")

    assignment.status = "finished"
    assignment.save()

    task.progress_status = "worker_done"
    task.save()

    return TaskServiceResult(
        message=f"작업 #{task.id} 를 작업 완료로 제출했습니다. 검수 신청이 가능해졌습니다."
    )


def mark_review_done(task: Task, profile: UserProfile) -> TaskServiceResult:
    """
    reviewer 가 '검수 완료'를 처리하는 도메인 로직.
    - 현재 본인이 reviewer/active 로 배정되어 있어야 함
    - Task.progress_status == review 인 경우만 허용
    - 완료 후:
        해당 TaskAssignment.status = finished
        Task.progress_status = review_done
    """
    if profile.role != "reviewer":
        raise TaskServiceError("검수 완료 처리를 할 권한이 없습니다.")

    try:
        assignment = TaskAssignment.objects.get(
            task=task,
            user=profile,
            role="reviewer",
            status="active",
        )
    except TaskAssignment.DoesNotExist:
        raise TaskServiceError("이 작업의 담당 검수자가 아닙니다.")

    if task.progress_status != "review":
        raise TaskServiceError("검수 중인 상태의 작업만 검수 완료로 처리할 수 있습니다.")

    assignment.status = "finished"
    assignment.save()

    task.progress_status = "review_done"
    task.save()

    return TaskServiceResult(
        message=f"작업 #{task.id} 검수를 완료했습니다."
    )
