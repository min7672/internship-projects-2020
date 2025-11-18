# Django Architecture Summary (TIL)

## 1. Spring ↔ Django Layer Mapping

| Spring              | Django                              | 설명                           |
| ------------------- | ----------------------------------- | ------------------------------ |
| Controller          | **View** (FBV/CBV/DRF View)             | HTTP Request/Response 처리      |
| **Service**             | app/services/*.py                   | 비즈니스 흐름 조립 (UseCase)     |
| **Repository**          | Model + Manager/QuerySet            | Django ORM이 Repository 역할     |
| Entity/Domain       | **Model**                               | 도메인 메서드 포함 가능          |
| View (JSP, Thymeleaf) | **Template**                          | 사용자 UI (HTML)                |
| **DTO**                 | Form / Serializer                   | Request 검증/데이터 구조 정의     |
| External Adapter    | app/infrastructure/*.py             | 외부 API/소셜로그인/저장소 연동   |

--- 

## 2. Django Core Philosophy (요약)

1) **Fast development**  
   - 생산성·신속한 개발 중심, 내장 기능 제공

2) **Loose coupling**  
   - **ORM**·View·Template·URL 간 결합 최소화

3) **Tight cohesion**  
   - 각 요소는 단일 책임에 집중

4) **DRY**  
   - 중복 최소화, 재사용 극대화

5) **Explicit is better than implicit**  
   - 동작을 명시적으로 표현하는 방식 선호

6) **Pluggability & reusability**  
   - 앱 단위로 분리·재사용 가능

7) **Secure by design**  
   - 보안 **기능 내장** (XSS, CSRF 등)

8) **Scalable architecture**  
   - 요청-응답 기반, 수평 확장 용이

9) **MVT pattern**  
   - **Model: 데이터 및 도메인 규칙**
   - View: 요청·응답 처리  
   - Template: 화면 표현


---

## 3. Service & Infrastructure Layer (실무 확장 시 역할)

### 3-1. Service Layer (services/)

**역할**
- View로부터 비즈니스 흐름 분리  
- 도메인 모델 조합  
- 트랜잭션 처리  
- 규칙 기반 UseCase 정의  
- View는 서비스 호출만 담당

**예시**

```python
# app/services/order_service.py

from django.db import transaction
from app.models import Order, Product

@transaction.atomic
def create_order_for_user(user, product_id, quantity: int) -> Order | None:
    product = Product.objects.filter(id=product_id, is_active=True).first()
    if product is None:
        return None

    order = Order.objects.create(
        user=user,
        product=product,
        quantity=quantity,
        total_price=product.price * quantity,
    )
    return order
```

## 3-2. Infrastructure Layer (infrastructure/)

**역할**

- 외부 시스템 연동(소셜 로그인, API, 통신)
- 기술 의존 코드 분리
- Django/비즈니스 로직과 독립적 위치
- 서비스 레이어가 이를 호출해 사용

**예시**

```python
# app/infrastructure/external_api_client.py

import requests

class ExternalApiClient:
    BASE_URL = "https://api.example.com"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_user_profile(self, external_user_id: str) -> dict:
        url = f"{self.BASE_URL}/users/{external_user_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.get(url, headers=headers, timeout=3)
        response.raise_for_status()
        return response.json()
```

### 3-3. View에서 Service를 사용하는 간단 패턴

```python
# app/views/order_views.py

from django.shortcuts import redirect
from app.services.order_service import create_order_for_user

def create_order_view(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity", "1"))

        order = create_order_for_user(request.user, product_id, quantity)
        # 이후 처리 (성공/실패 분기, 리다이렉트 등)
        return redirect("order:list")

    # GET 요청일 경우 폼 페이지 렌더링 등

```

### 3-4. Authentication Layer (authentication/)

**역할**

- 요청에서 인증 정보(Session, JWT 등)를 읽어 사용자 식별
- 토큰/세션 검증 후 request.user 설정
- 인증 방식(Session/JWT/OAuth)을 서비스/도메인 로직과 분리

```bash
app/
├── authentication/                     # 인증 계층 (JWT/세션/OAuth 등 인증 처리)
│     ├── jwt_middleware.py             # 요청에서 JWT 추출·검증, request.user 설정
│     ├── jwt_auth_backend.py           # JWT payload 기반 사용자 조회 로직
│     └── token_utils.py                # JWT encode/decode·만료 검증 유틸
│
├── services/                            # 비즈니스 로직 계층 (UseCase 단위)
│     ├── user_service.py                # 사용자 관련 도메인 규칙 및 처리 흐름
│     └── task_service.py                # 작업(Task) 관련 도메인 로직 및 트랜잭션 처리
│
├── infrastructure/                      # 외부 시스템 연동 계층
│     ├── social_oauth.py                # 카카오/구글 등 외부 OAuth API 호출 모듈
│
├── views.py                             # HTTP 요청 처리, 서비스 호출, 응답 반환
└── models.py                            # 도메인 모델 정의 및 ORM 매핑

```