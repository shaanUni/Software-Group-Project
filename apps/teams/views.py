from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q

from .forms import TeamCreateForm, UserCreateForm, DepartmentCreateForm, ProjectCreateForm
from .models import Department, Team
from .audit import log_audit_event

def is_superadmin(user):
    return user.is_authenticated and user.is_superuser


@login_required
def team_list(request):
    teams = Team.objects.select_related("team_leader", "department")
    query = request.GET.get('q', '').strip()
    
    if query:
        teams = teams.filter(
            Q(team_name__icontains=query) |
            Q(department__department_name__icontains=query) |
            Q(team_leader__username__icontains=query) |
            Q(team_leader__first_name__icontains=query) |
            Q(team_leader__last_name__icontains=query)
        )
    
    return render(request, "teams/list.html", {"teams": teams, "query": query})


@login_required
@user_passes_test(is_superadmin)
def superadmin_team_create(request, department_id=None):
    if request.method == "POST":
        form = TeamCreateForm(request.POST)
        if form.is_valid():
            team = form.save()

            log_audit_event(
                user=request.user,
                action="CREATE",
                obj=team,
                description=f"Created team '{team}'.",
            )
            messages.success(request, "Team created successfully.")
            return redirect("team-list")
    else:
        initial = {}
        if department_id:
            from .models import Department
            try:
                department = Department.objects.get(pk=department_id)
                initial = {"department": department}
            except Department.DoesNotExist:
                pass
        form = TeamCreateForm(initial=initial)

    return render(request, "teams/superadmin_team_create.html", {"form": form})


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
        old_name = str(team)
        if form.is_valid():
            updated_team = form.save()
            log_audit_event(
                user=request.user,
                action="UPDATE",
                obj=updated_team,
                description=f"Updated team '{old_name}' to '{updated_team}'.",
            )
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
            new_user = form.save()
            log_audit_event(
                user=request.user,
                action="CREATE",
                obj=new_user,
                description=f"Created user '{new_user}'.",
            )
            messages.success(request, "User created successfully.")
            return redirect("user-create")
    else:
        form = UserCreateForm()

    return render(request, "teams/user_create.html", {"form": form})

def organisation_view(request):
    teams = Team.objects.select_related("downstream_dependency", "department").all().order_by("team_name")

    team_data = [
        {
            "id": team.team_id,
            "name": team.team_name or f"Team {team.team_id}",
            "department": team.department.department_name if team.department else None,
            "members": team.employee_count(),
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

@login_required
@user_passes_test(is_superadmin)
def department_create_view(request):
    if request.method == "POST":
        form = DepartmentCreateForm(request.POST)

        if form.is_valid():
            department = form.save()

            log_audit_event(
                user=request.user,
                action="CREATE",
                obj=department,
                description=f"Created department '{department}'.",
            )

            messages.success(request, "Department created successfully.")
            return redirect("department-list")
    else:
        form = DepartmentCreateForm()

    return render(
        request,
        "teams/simple_form.html",
        {
            "form": form,
            "page_title": "Create Department",
            "page_subtitle": "Add a new department.",
            "submit_text": "Create Department",
"cancel_url": "department-list",
        },
    )


@login_required
def department_list(request):
    from django.db.models import Count

    try:
        departments = Department.objects.select_related("department_head").annotate(
            team_count=Count("teams")
        )

        query = request.GET.get('q', '').strip()
        sort = request.GET.get('sort', 'name')

        if query:
            departments = departments.filter(
                Q(department_name__icontains=query) |
                Q(department_head__username__icontains=query) |
                Q(department_head__first_name__icontains=query) |
                Q(department_head__last_name__icontains=query)
            )

        if sort == 'teams':
            departments = departments.order_by("-team_count", "department_name")
        else:
            departments = departments.order_by("department_name")

        department_list = list(departments)
    except Exception as e:
        import traceback
        traceback.print_exc()
        department_list = []

    return render(
        request,
        "teams/department_list.html",
        {
            "departments": department_list,
            "query": query,
            "sort": sort,
        },
    )


@login_required
@login_required
def department_detail(request, department_id):
    department = get_object_or_404(
        Department.objects.select_related("department_head"),
        pk=department_id,
    )

    teams = Team.objects.select_related("team_leader", "downstream_dependency").filter(
        department=department
    ).order_by("team_name")

    teams_with_deps = []
    for team in teams:
        upstream_teams = team.upstream_teams.select_related("department").all()
        downstream_team = team.downstream_dependency

        teams_with_deps.append({
            "team": team,
            "upstream_teams": upstream_teams,
            "downstream_team": downstream_team,
        })

    return render(
        request,
        "teams/department_detail.html",
        {
            "department": department,
            "teams": teams_with_deps,
        },
    )


@login_required
@user_passes_test(is_superadmin)
def project_create_view(request):
    if request.method == "POST":
        form = ProjectCreateForm(request.POST)

        if form.is_valid():
            project = form.save()

            log_audit_event(
                user=request.user,
                action="CREATE",
                obj=project,
                description=f"Created project '{project}'.",
            )

            messages.success(request, "Project created successfully.")
            return redirect("team-list")
    else:
        form = ProjectCreateForm()

    return render(
        request,
        "teams/simple_form.html",
        {
            "form": form,
            "page_title": "Create Project",
            "page_subtitle": "Add a new project and assign it to a team.",
            "submit_text": "Create Project",
"cancel_url": "department-list",
        },
    )