from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render, redirect

from .forms import TeamCreateForm, EmployeeCreateForm
from .models import Team, Employee


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
        Team.objects.select_related("team_leader", "department").prefetch_related("employees"),
        pk=team_id,
    )
    
    employees = team.employees.all()

    return render(request, "teams/detail.html", {"team": team, "employees": employees,})

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
def employee_create_view(request):
    if request.method == "POST":
        form = EmployeeCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Employee created successfully.")
            return redirect("employee-create")
    else:
        form = EmployeeCreateForm()

    return render(request, "teams/employee_create.html", {"form": form})

