# editor/infrastructure/signals.py

from django.dispatch import receiver
from allauth.socialaccount.signals import social_account_added
from allauth.socialaccount.models import SocialLogin
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from .social_oauth import ensure_user_profile_for_social_login
from editor.models import UserProfile


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



@receiver(post_save, sender=get_user_model())
def ensure_user_profile_for_normal_user(sender, instance, created, **kwargs):
    """
    일반 User 생성 시(User.objects.create, createsuperuser 등)에도
    UserProfile 이 항상 존재하도록 보장.
    소셜 계정이 없는 유저용 fallback.
    """
    if not created:
        return

    # 이미 프로필 있으면 건드리지 않음
    if hasattr(instance, "profile"):
        return

    UserProfile.objects.create(
        user=instance,
        email_address=instance.email or "",
        phone_number="",
        is_approved=False,
        role="worker",
        extra_data={},
    )

"""
from django.contrib.auth import get_user_model
from editor.models import UserProfile

User = get_user_model()

count = 0

for u in User.objects.all():
    if not hasattr(u, "profile"):
        UserProfile.objects.create(
            user=u,
            email_address=u.email or "",
            phone_number="",
            is_approved=False,
            role="worker",
            extra_data={},
        )
        count += 1

print(f"자동 생성된 UserProfile 개수: {count}")
"""