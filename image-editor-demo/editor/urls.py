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

    # 작업 관련 페이지
    path("tasks/", views.task_list, name="task_list"),
    path("reviews/", views.review_list, name="review_list"),
    path("tasks/overview/", views.task_overview, name="task_overview"),
]
