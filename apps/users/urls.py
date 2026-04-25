from django.urls import path, reverse_lazy
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
from .forms import (
    AdminLoginForm,
    MemberLoginForm,
    SkyPasswordResetForm,
    SkySetPasswordForm,
)

urlpatterns = [
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path(
        "admin-login/",
        auth_views.LoginView.as_view(
            template_name="registration/admin_login.html",
            authentication_form=AdminLoginForm,
            redirect_authenticated_user=True,
        ),
        name="admin-login",
    ),
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
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="users/account_password_reset_form.html",
            email_template_name="users/account_password_reset_email.html",
            subject_template_name="users/account_password_reset_subject.txt",
            form_class=SkyPasswordResetForm,
            success_url=reverse_lazy("account-password-reset-done"),
        ),
        name="account-password-reset",
    ),
    path(
        "password-reset/sent/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="users/account_password_reset_done.html"
        ),
        name="account-password-reset-done",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="users/account_password_reset_confirm.html",
            form_class=SkySetPasswordForm,
            success_url=reverse_lazy("account-password-reset-complete"),
        ),
        name="account-password-reset-confirm",
    ),
    path(
        "password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="users/account_password_reset_complete.html"
        ),
        name="account-password-reset-complete",
    ),
]
