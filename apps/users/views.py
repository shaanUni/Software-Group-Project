from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render

from apps.teams.models import Team

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


@user_passes_test(is_admin_user)
def admin_dashboard(request):
    return render(request, "users/admin_dashboard.html")


@user_passes_test(is_admin_user)
def admin_user_management(request):
    User = get_user_model()
    teams = Team.objects.order_by("team_name", "team_id")

    if request.method == "POST":
        action = request.POST.get("action")
        user_id = request.POST.get("user_id")
        target_user = User.objects.select_related("team").filter(pk=user_id).first()

        if not target_user:
            messages.error(request, "That user could not be found.")
            return redirect("admin-user-management")

        if action == "delete":
            if not request.user.is_superuser:
                messages.error(request, "Only superusers can delete users.")
            elif target_user.pk == request.user.pk:
                messages.error(request, "You cannot delete your own account from here.")
            else:
                target_user.delete()
                messages.success(request, f"Deleted user {target_user.username}.")
            return redirect("admin-user-management")

        if action == "update":
            target_user.team_id = request.POST.get("team_id") or None

            if request.user.is_superuser:
                if target_user.pk == request.user.pk:
                    target_user.is_staff = True
                    target_user.is_superuser = True
                    target_user.is_active = True
                else:
                    target_user.is_staff = request.POST.get("is_staff") == "on"
                    target_user.is_superuser = request.POST.get("is_superuser") == "on"
                    target_user.is_active = request.POST.get("is_active") == "on"

            target_user.save()
            messages.success(request, f"Updated user {target_user.username}.")
            return redirect("admin-user-management")

        messages.error(request, "Unknown action requested.")
        return redirect("admin-user-management")

    users = User.objects.select_related("team").order_by("username")

    return render(
        request,
        "users/admin_user_management.html",
        {
            "users": users,
            "teams": teams,
        },
    )


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