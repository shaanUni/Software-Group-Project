from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect

from .forms import TeamCreateForm
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

    return render(request, "teams/superadmin_team_create.html", {"form": form})