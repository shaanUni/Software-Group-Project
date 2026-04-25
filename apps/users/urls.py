from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    register_view,
    dashboard_router,
    user_dashboard,
    admin_dashboard,
    admin_user_management,
    profile_view,
    edit_profile_view,
)

urlpatterns = [
    path("register/", register_view, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    path("dashboard/", dashboard_router, name="dashboard-router"),
    path("dashboard/user/", user_dashboard, name="user-dashboard"),
    path("dashboard/admin/", admin_dashboard, name="admin-dashboard"),
    path("dashboard/admin/users/", admin_user_management, name="admin-user-management"),

    path("profile/", profile_view, name="profile"),
    path("profile/edit/", edit_profile_view, name="edit_profile"),

    path(
        "password-change/",
        auth_views.PasswordChangeView.as_view(
            template_name="registration/password_change.html"
        ),
        name="password_change",
    ),
    path(
        "password-change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="registration/password_change_done.html"
        ),
        name="password_change_done",
    ),
]