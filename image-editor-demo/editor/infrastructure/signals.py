# editor/infrastructure/signals.py

from django.dispatch import receiver
from allauth.socialaccount.signals import social_account_added
from allauth.socialaccount.models import SocialLogin

from .social_oauth import ensure_user_profile_for_social_login


@receiver(social_account_added)
def handle_social_account_added(request, sociallogin: SocialLogin, **kwargs):
    """
    allauth: 소셜 계정이 추가될 때 발생하는 시그널.
    - 여기서는 인프라 연결만 담당
    - 실제 프로필 생성/정리는 social_oauth 헬퍼에 위임
    """
    user = sociallogin.user
    socialaccount = sociallogin.account
    ensure_user_profile_for_social_login(user, socialaccount)
