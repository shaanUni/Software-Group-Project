from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    register_view,
    login_view,
    dashboard_router,
    user_dashboard,
    admin_dashboard,
    admin_user_management,
    admin_user_detail,
    profile_view,
    edit_profile_view,
)

urlpatterns = [
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    path("dashboard/", dashboard_router, name="dashboard-router"),
    path("dashboard/user/", user_dashboard, name="user-dashboard"),
    path("dashboard/admin/", admin_dashboard, name="admin-dashboard"),
    path("dashboard/admin/users/", admin_user_management, name="admin-user-management"),
    path("dashboard/admin/users/<int:user_id>/", admin_user_detail, name="admin-user-detail"),

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