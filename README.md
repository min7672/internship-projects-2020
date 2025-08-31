# Internship Project Archive

본 저장소는 인턴십 기간 동안 수행했던 프로젝트 중, 주요 성과를 정리한 아카이브입니다.  
실제 프로젝트를 기반으로 하되, 보안 및 데이터 노출 우려가 있는 부분은 제외하거나 단순화하여 **데모 형태**로 재현하였습니다.  

## 저장소 구조
```
.
|-- README.md                # 최상위 소개 문서
|-- audio_converter/         # 오디오 변환 도구 (ffmpeg + PyQt5 기반)
|-- image-editor-demo/       # 웹 기반 의료 영상 어노테이션 툴 데모
```

## 프로젝트 소개

### 1. Audio Converter
- **개요**: 방언 학습데이터 구축 사업에서, 웹 무료 파일 변환기의 비효율성을 대체하기 위해 개발한 내부용 변환 툴  
- **기능**: mp3/m4a → wav → pcm 변환 (wav 헤더 제거 방식), 파일/폴더 단위 변환 지원  
- **기술 스택**: Python, PyQt5, ffmpeg  
- [자세히 보기](./audio_converter/README.md)

### 2. Image Editor Demo
- **개요**: 의료 영상(PET-CT) 데이터를 웹 환경에서 어노테이션하기 위한 사용자 참여형 툴의 데모 구현  
- **기능**: 마우스 이벤트 기반 이미지 편집, 웹 UI(jQuery/HTML/CSS), Django 연동 일부 재현  
- **기술 스택**: Django, jQuery, HTML5, CSS3, (Infra: Ubuntu, Nginx, Gunicorn, PostgreSQL)  
- [자세히 보기](./image-editor-demo/README.md)

## 실행 및 사용
- 각 디렉토리(`audio_converter/`, `image-editor-demo/`) 내에 별도의 `README.md`에서 상세 실행 방법과 설명을 확인할 수 있습니다.

## 특이사항
- 본 저장소는 인턴십 당시의 **성과 및 구현 경험을 회고성으로 정리**한 것입니다.  
- 일부 기능은 보안 및 데이터 테이블 노출 우려로 데모에서 제외되었으며, 실제 프로젝트와 차이가 있을 수 있습니다.  
