# editor/infrastructure/social_oauth.py

from allauth.socialaccount.models import SocialAccount
from editor.models import UserProfile


def extract_basic_profile_from_social(socialaccount: SocialAccount) -> dict:
    """
    소셜 계정에서 기본 프로필 정보 추출.
    provider(카카오/구글 등)에 따라 필드명이 다를 수 있으므로 여기서 정리.
    """
    data = socialaccount.extra_data or {}

    # 카카오 예시
    if socialaccount.provider == "kakao":
        kakao_account = data.get("kakao_account", {})
        profile = kakao_account.get("profile", {})
        email = kakao_account.get("email")
        name = profile.get("nickname") or data.get("properties", {}).get("nickname")

    else:
        # 기타 provider 공통 fallback
        email = data.get("email")
        name = data.get("name")

    return {
        "email": email,
        "name": name,
        "raw": data,
    }


def ensure_user_profile_for_social_login(user, socialaccount: SocialAccount) -> UserProfile:
    """
    소셜 로그인 성공 이후 UserProfile을 보장한다.
    - 이미 있으면 그대로 반환
    - 없으면 새로 생성
    """
    extracted = extract_basic_profile_from_social(socialaccount)

    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            "email_address": extracted["email"] or user.email,
            "phone_number": "",
            "is_approved": False,
            "role": "worker",
            "extra_data": extracted["raw"] or {},
        },
    )

    # 필요하면 이후에 role / 승인 상태 등 업데이트도 이것에서 처리 가능
    return profile
