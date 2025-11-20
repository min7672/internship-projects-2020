# editor/services/image_service.py
# [SVC-4] IMAGE-IO
# - 이미지 파일 로딩/인코딩 등 I/O 관련 헬퍼

import base64
from pathlib import Path


def encode_image_to_base64(path: str | Path) -> str:
    """이미지 파일을 base64 문자열로 변환."""
    file_path = Path(path)
    with file_path.open("rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")
