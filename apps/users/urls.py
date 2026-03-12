from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path(
        "login/",
        LoginView.as_view(
            template_name="users/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("dashboard/", views.dashboard_router, name="dashboard"),
    path("user-dashboard/", views.user_dashboard, name="user-dashboard"),
    path("admin-dashboard/", views.admin_dashboard, name="admin-dashboard"),
]