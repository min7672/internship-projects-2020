# editor/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=50, required=False)

    class Meta:
        model = User
        fields = ("email", "phone_number", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]   # username을 이메일로 강제
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()

            UserProfile.objects.create(
                user=user,
                email_address=self.cleaned_data["email"],
                phone_number=self.cleaned_data["phone_number"],
                is_approved=False,
                role="worker",
                extra_data={}
            )

        return user
