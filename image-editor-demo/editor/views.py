from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import SignupForm


def home(request):
    return render(request, "page/home.html")


def login_page(request):
    if request.method == "POST":
        email = request.POST.get("login")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect("home")

        return render(request, "page/login.html", {
            "error": "이메일 또는 비밀번호가 맞지 않습니다."
        })

    return render(request, "page/login.html")


def logout_page(request):
    logout(request)
    return redirect("home")


def signup_page(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "회원가입이 완료되었습니다. 관리자 승인 후 로그인할 수 있습니다.")
            return redirect("login")
    else:
        form = SignupForm()

    return render(request, "page/signup.html", {"form": form})


@login_required
def mypage(request):
    return render(request, "page/mypage.html")


@login_required
def task_list(request):
    return render(request, "page/task_list.html")


@login_required
def review_list(request):
    return render(request, "page/review_list.html")


@login_required
def task_overview(request):
    return render(request, "page/task_overview.html")
