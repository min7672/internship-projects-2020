"""
===============================================================
                        editor/views.py
===============================================================
    설명                                                태그
   - 1) 인증/Auth 관련                                  AuthController
   - 2) 사용자 프로필 / 마이페이지                        UserController
   - 3) Task 조회·목록 관련 (Worker/Reviewer/Admin)     TaskQueryController
   - 4) Task 작업 화면 (이미지 로딩)                     TaskWorkController
   - 5) Task 상태 변경 액션                             TaskActionController
===============================================================
"""

from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.conf import settings
import os

from .models import Task, TaskAssignment
from .forms import SignupForm
from editor.services.task_service import (
    apply_task,
    approve_task,
    mark_work_done,
    mark_review_done,
    TaskServiceError,
)
from editor.services.task_view_service import (
    decorate_task_action_for_user,
)
from editor.services.patient_service import (
    attach_masked_patient_id,
)
from editor.services.image_service import (
    encode_image_to_base64,
)


# ===================================================================
# 1) 계정 / 인증 컨트롤러 (AuthController)
# ===================================================================

def home(request):
    return render(request, "page/home.html")

def signup_page(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "회원가입이 완료되었습니다. 관리자 승인 후 로그인할 수 있습니다.",
            )
            return redirect("login")
    else:
        form = SignupForm()

    return render(request, "page/signup.html", {"form": form})

def login_page(request):
    if request.method == "POST":
        email = request.POST.get("login")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect("home")

        return render(
            request, "page/login.html",
            {"error": "이메일 또는 비밀번호가 맞지 않습니다."},
        )

    return render(request, "page/login.html")

def logout_page(request):
    logout(request)
    return redirect("home")


# ===================================================================
# 2) 사용자 프로필 / 마이페이지 (UserController)
# ===================================================================

@login_required
def mypage(request):
    return render(request, "page/mypage.html")


# ===================================================================
# 3) Task 조회 / 목록 / 검색 / 페이지네이션 (TaskQueryController)
# ===================================================================

@login_required
def task_list(request):
    profile = request.user.profile

    # 기본 Task 쿼리
    qs = Task.objects.all()
    pending_assignments = []

    # 역할별 필터링
    if profile.role == "admin":
        pending_assignments = (
            TaskAssignment.objects.filter(status="pending")
            .select_related("task", "user")
            .order_by("-assigned_at")
        )
    elif profile.role == "worker":
        qs = qs.exclude(progress_status="worker_done").exclude(
            assignments__role="worker",
            assignments__status__in=["pending", "active", "finished"]
        )
    elif profile.role == "reviewer":
        qs = qs.filter(progress_status="worker_done").exclude(
            assignments__role="reviewer",
            assignments__status__in=["pending", "active", "finished"]
        )

    # 정렬
    sort = request.GET.get("sort", "created")
    direction = request.GET.get("dir", "desc")

    sort_map = {
        "id": "id",
        "title": "task_title",
        "reward": "reward",
        "request": "task_request",
        "created": "created_at",
        "progress_status": "progress_status",
    }
    sort_field = sort_map.get(sort, "created_at")
    if direction == "desc":
        sort_field = "-" + sort_field

    qs = qs.order_by(sort_field)

    # 페이지네이션
    try:
        per_page = int(request.GET.get("per_page", 10))
    except ValueError:
        per_page = 10

    if per_page not in [10, 20, 50]:
        per_page = 10

    paginator = Paginator(qs, per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Action / Masking 정보 부착
    for task in page_obj:
        decorate_task_action_for_user(task, profile)
        attach_masked_patient_id(task)

    return render(
        request, "page/task_list.html",
        {
            "page_obj": page_obj,
            "sort": sort,
            "direction": direction,
            "per_page": per_page,
            "is_admin": profile.role == "admin",
            "role": profile.role,
            "pending_assignments": pending_assignments,
        }
    )


@login_required
def mytask(request):
    profile = request.user.profile

    my_assignments = (
        TaskAssignment.objects.filter(user=profile)
        .select_related("task")
        .order_by("-assigned_at")
    )

    try:
        per_page = int(request.GET.get("per_page", 10))
    except ValueError:
        per_page = 10

    if per_page not in [10, 20, 50]:
        per_page = 10

    paginator = Paginator(my_assignments, per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    tasks = []
    for ass in page_obj:
        task = ass.task
        decorate_task_action_for_user(task, profile)
        attach_masked_patient_id(task)
        tasks.append({"task": task, "assignment": ass})

    return render(
        request, "page/mytask.html",
        {"tasks": tasks, "page_obj": page_obj, "per_page": per_page, "role": profile.role},
    )

@login_required
def review_list(request):
    profile = request.user.profile

    qs = (
        TaskAssignment.objects.filter(user=profile, role="reviewer")
        .select_related("task")
    )

    sort = request.GET.get("sort", "id")
    direction = request.GET.get("dir", "desc")
    ordering = f"-{sort}" if direction == "desc" else sort
    qs = qs.order_by(ordering)

    per_page = int(request.GET.get("per_page", 10))
    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(request.GET.get("page"))

    for item in page_obj:
        decorate_task_action_for_user(item.task, profile)
        attach_masked_patient_id(item.task)

    return render(
        request, "page/review_list.html",
        {
            "page_obj": page_obj,
            "per_page": per_page,
            "sort": sort,
            "direction": direction,
        }
    )

# ===================================================================
# 4) Task 작업 화면 / 이미지 로딩 (TaskWorkController)
# ===================================================================

@login_required
def task_work(request, task_id):

    folder_rel_path = os.path.join("img", "png", "CT", "CT_LC09548")
    folder_abs_path = os.path.join(settings.MEDIA_ROOT, folder_rel_path)

    pet_b64 = ""
    ct_b64 = ""
    images = []

    if os.path.isdir(folder_abs_path):
        file_names = sorted(
            f for f in os.listdir(folder_abs_path)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        )
        images = file_names

        if file_names:
            pet_path = os.path.join(folder_abs_path, file_names[0])
            pet_b64 = encode_image_to_base64(pet_path)

            if len(file_names) > 1:
                ct_path = os.path.join(folder_abs_path, file_names[1])
                ct_b64 = encode_image_to_base64(ct_path)
            else:
                ct_b64 = pet_b64

    return render(
        request,
        "page/task_work.html",
        {
            "pet_image_b64": pet_b64,
            "ct_image_b64": ct_b64,
            "last_capture": None,
            "current_index": 1,
            "total_count": len(images),
        },
    )


# ===================================================================
# 5) Task 상태 변경 액션 (TaskActionController)
# ===================================================================

@login_required
def task_apply(request, task_id):
    if request.method != "POST":
        return redirect("task_list")

    profile = request.user.profile
    task = get_object_or_404(Task, id=task_id)

    try:
        result = apply_task(task, profile)
        messages.success(request, result.message)
    except TaskServiceError as e:
        messages.error(request, str(e))

    return redirect("task_list")


@login_required
def task_approve(request, task_id):
    if request.method != "POST":
        return redirect("task_list")

    profile = request.user.profile
    task = get_object_or_404(Task, id=task_id)

    try:
        result = approve_task(task, profile)
        messages.success(request, result.message)
    except TaskServiceError as e:
        messages.error(request, str(e))

    return redirect("task_list")


@login_required
def work_done(request, task_id):
    if request.method != "POST":
        return redirect("task_list")

    profile = request.user.profile
    task = get_object_or_404(Task, id=task_id)

    try:
        result = mark_work_done(task, profile)
        messages.success(request, result.message)
    except TaskServiceError as e:
        messages.error(request, str(e))

    return redirect("task_list")


@login_required
def review_done(request, task_id):
    if request.method != "POST":
        return redirect("task_list")

    profile = request.user.profile
    task = get_object_or_404(Task, id=task_id)

    try:
        result = mark_review_done(task, profile)
        messages.success(request, result.message)
    except TaskServiceError as e:
        messages.error(request, str(e))

    return redirect("task_list")
