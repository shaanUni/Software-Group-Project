from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render

from .forms import RegisterForm, UserUpdateForm


def is_admin_user(user):
    return user.is_authenticated and user.is_staff


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard-router")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your account has been created successfully.")
            return redirect("dashboard-router")
    else:
        form = RegisterForm()

    return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard_router(request):
    if request.user.is_staff:
        return redirect("admin-dashboard")
    return redirect("user-dashboard")


@login_required
def user_dashboard(request):
    return render(request, "users/user_dashboard.html")


@user_passes_test(is_admin_user, login_url="/users/login/")
def admin_dashboard(request):
    return render(request, "users/admin_dashboard.html")


@login_required
def profile_view(request):
    return render(request, "registration/profile.html")


@login_required
def edit_profile_view(request):
    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("profile")
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, "registration/edit_profile.html", {"form": form})