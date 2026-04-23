from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render, redirect

from .forms import TeamCreateForm, UserCreateForm
from .models import Team


def is_superadmin(user):
    return user.is_authenticated and user.is_superuser


@login_required
def team_list(request):
    teams = Team.objects.select_related("team_leader", "department")
    return render(request, "teams/list.html", {"teams": teams})


@login_required
@user_passes_test(is_superadmin)
def superadmin_team_create(request):
    if request.method == "POST":
        form = TeamCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Team created successfully.")
            return redirect("team-list")
    else:
        form = TeamCreateForm()

    return render(request, "teams/team_form.html", {"form": form})


@login_required
def team_detail(request, team_id):
    team = get_object_or_404(
        Team.objects.select_related("team_leader", "department").prefetch_related("users"),
        pk=team_id,
    )

    users = team.users.all()

    return render(
        request,
        "teams/detail.html",
        {
            "team": team,
            "users": users,
        },
    )


@login_required
@user_passes_test(is_superadmin)
def team_edit_view(request, pk):
    team = get_object_or_404(Team, pk=pk)

    if request.method == "POST":
        form = TeamCreateForm(request.POST, instance=team)
        if form.is_valid():
            form.save()
            messages.success(request, "Team updated successfully.")
            return redirect("team-list")
    else:
        form = TeamCreateForm(instance=team)

    return render(
        request,
        "teams/team_form.html",
        {
            "form": form,
            "page_title": "Edit Team",
            "page_subtitle": "Update the team details below.",
            "submit_text": "Save Changes",
            "is_edit": True,
            "team": team,
        },
    )


@login_required
@user_passes_test(is_superadmin)
def user_create_view(request):
    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User created successfully.")
            return redirect("user-create")
    else:
        form = UserCreateForm()

    return render(request, "teams/user_create.html", {"form": form})

def organisation_view(request):
    teams = Team.objects.select_related("downstream_dependency").all().order_by("team_name")

    team_data = [
        {
            "id": team.team_id,
            "name": team.team_name or f"Team {team.team_id}",
            "downstream_dependency_id": (
                team.downstream_dependency.team_id if team.downstream_dependency else None
            ),
        }
        for team in teams
    ]

    return render(
        request,
        "teams/organisation.html",
        {
            "teams": teams,
            "team_data": team_data,
        },
    )