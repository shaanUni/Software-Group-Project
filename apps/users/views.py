from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render


def is_admin_user(user):
    return user.is_authenticated and user.is_staff


@login_required
def dashboard_router(request):
    if request.user.is_staff:
        return redirect("admin-dashboard")
    return redirect("user-dashboard")


@login_required
def user_dashboard(request):
    return render(request, "users/user_dashboard.html")


@user_passes_test(is_admin_user, login_url="/login/")
def admin_dashboard(request):
    return render(request, "users/admin_dashboard.html")