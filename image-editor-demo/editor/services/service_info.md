### 1. services 디렉토리 

``` bash
editor/
└─ services/
   ├─ __init__.py
   ├─ task_service.py         # [SVC-1] TASK-STATE      (상태 전환 / 도메인 로직)
   ├─ task_view_service.py    # [SVC-2] TASK-UI         (목록/버튼 라벨 등 뷰모델)
   ├─ patient_service.py      # [SVC-3] PATIENT-ID      (환자 ID 추출/마스킹)
   ├─ image_service.py        # [SVC-4] IMAGE-IO        (png/base64, dicom→png, 개수)
```