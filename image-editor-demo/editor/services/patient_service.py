# editor/services/patient_service.py
# [SVC-3] PATIENT-ID
# - Task 기반 환자 ID 추출 및 마스킹

from editor.models import Task


def _extract_patient_id_from_task(task: Task) -> str:
    """
    Task 에서 환자 고유 식별자(예: CT_LC09548)를 추출한다.
    - 우선 CT 경로에서 디렉토리 마지막 이름 사용
      예) media/img/CT/CT_LC09548 -> CT_LC09548
    - 없으면 PET 경로에서 사용
    """
    path = task.task_path_CT or task.task_path_PET
    if not path:
        return ""

    # 끝의 디렉토리/파일 이름만 사용
    raw = path.rstrip("/").split("/")[-1]
    return raw


def _mask_patient_id(pid: str) -> str:
    """
    환자 식별자 마스킹 규칙.
    예) CT_LC09548 -> CT_LC09******
    """
    if not isinstance(pid, str) or not pid:
        return ""

    if len(pid) <= 3:
        return "***"

    # 뒤 6자리 마스킹
    return pid[:-6] + "******"


def attach_masked_patient_id(task: Task) -> None:
    """
    Task 인스턴스에 patient_id_masked 속성을 동적으로 붙여준다.
    템플릿에서는 task.patient_id_masked 만 사용하면 된다.
    """
    raw_id = _extract_patient_id_from_task(task)
    task.patient_id_masked = _mask_patient_id(raw_id)
