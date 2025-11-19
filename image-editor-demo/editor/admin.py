# editor/admin.py (예시)

from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import UserProfile, Task, TaskAssignment


User = get_user_model()


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ( "id", "user", "role", "email_address", "phone_number", "created_at", )

    list_filter = ("role", )

    search_fields = ("user__username", "user__email", "email_address")

    ordering = ("-created_at",)


class TaskAssignmentInline(admin.TabularInline):
    model = TaskAssignment
    extra = 1
    autocomplete_fields = ("user",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ( "id", "task_title", "task_type", "progress_status", "reward", "pre_task", "ins_task_1", "task_rate", "created_at", )
    list_filter = ("task_type", "progress_status",)
    search_fields = ("task_title", "task_request")
    ordering = ("-created_at",)

    inlines = [TaskAssignmentInline]


@admin.register(TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):
    """
    Task 와 UserProfile 의 배정 관계를 직접 수정/조회하는 Admin
    - 리스트에서 role 을 바로 수정할 수 있게 list_editable 사용
    """
    list_display = ( "id", "task", "user", "role", "status","assigned_at", )
    list_filter = ("role","status")
    search_fields = ( "task__task_title", "user__user__username", "user__email_address", 
                     )
    ordering = ("-assigned_at",)

    list_editable = ("role",)
    list_display_links = ("id", "task")
