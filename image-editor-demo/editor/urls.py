# editor/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 메인 홈
    path("", views.home, name="home"),

    path("login/", views.login_page, name="login"),
    path("logout/", views.logout_page, name="logout"),
    path("signup/", views.signup_page, name="signup"),

    # 마이페이지
    path("mypage/", views.mypage, name="mypage"),
    path("mytask/", views.mytask, name="mytask"),

    # 작업 관련 페이지
    path("tasks/", views.task_list, name="task_list"),
    path("tasks/<int:task_id>/apply/", views.task_apply, name="task_apply"),
    path("reviews/", views.review_list, name="review_list"),
    path("tasks/<int:task_id>/approve/", views.task_approve, name="task_approve"),
    path("task/<int:task_id>/work/", views.task_work, name="task_work"),
]
