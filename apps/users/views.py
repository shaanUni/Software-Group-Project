from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import RegisterForm, UserUpdateForm
from apps.team_messages.models import TeamMessage
from apps.team_schedule.models import TeamMeeting
from apps.teams.models import Project, Team
from apps.teams.models import AuditTrail

def is_admin_user(user):
    return user.is_authenticated and user.is_staff


def _metric_value(value):
    return value if value else "-"


def _build_admin_activities(limit=4):
    activity_items = []

    for message in TeamMessage.objects.select_related("sender_team", "recipient_team").order_by("-created_at")[:10]:
        activity_items.append(
            {
                "title": f"Message: {message.subject}",
                "time": timezone.localtime(message.created_at),
                "display_time": timezone.localtime(message.created_at).strftime("%d %b %Y %H:%M"),
            }
        )

    for meeting in TeamMeeting.objects.select_related("team_one", "team_two").order_by("-created_at")[:10]:
        activity_items.append(
            {
                "title": f"Meeting created: {meeting.title}",
                "time": timezone.localtime(meeting.created_at),
                "display_time": timezone.localtime(meeting.created_at).strftime("%d %b %Y %H:%M"),
            }
        )

    activity_items.sort(key=lambda item: item["time"], reverse=True)
    return activity_items[:limit]


def _build_user_activities(user, limit=4):
    if not user.team:
        return []

    activity_items = []

    messages_qs = TeamMessage.objects.select_related("sender_team", "recipient_team").filter(
        recipient_team=user.team
    ).order_by("-created_at")[:10]
    for message in messages_qs:
        activity_items.append(
            {
                "title": f"New message: {message.subject}",
                "time": timezone.localtime(message.created_at),
                "display_time": timezone.localtime(message.created_at).strftime("%d %b %Y %H:%M"),
            }
        )

    meetings_qs = TeamMeeting.objects.select_related("team_one", "team_two").filter(
        team_one=user.team
    ) | TeamMeeting.objects.select_related("team_one", "team_two").filter(team_two=user.team)
    for meeting in meetings_qs.order_by("-created_at")[:10]:
        activity_items.append(
            {
                "title": f"Meeting created: {meeting.title}",
                "time": timezone.localtime(meeting.created_at),
                "display_time": timezone.localtime(meeting.created_at).strftime("%d %b %Y %H:%M"),
            }
        )

    activity_items.sort(key=lambda item: item["time"], reverse=True)
    return activity_items[:limit]


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
    user_team = request.user.team

    teams = list(
        Team.objects.select_related("department", "team_leader")
        .prefetch_related("users")
        .order_by("-team_id")[:3]
    )
    if user_team and all(team.pk != user_team.pk for team in teams):
        teams = [user_team] + teams[:2]

    recent_teams = [
        {
            "name": team.team_name or f"Team {team.team_id}",
            "manager": (
                team.team_leader.first_name
                or team.team_leader.username
                if team.team_leader
                else "-"
            ),
            "detail_url": f"/teams/{team.team_id}/",
        }
        for team in teams
    ]
    if not recent_teams:
        recent_teams = [{"name": "-", "manager": "-", "detail_url": "#"}]

    recent_updates = AuditTrail.objects.select_related("admin_user").order_by("-created_at")[:4]

    quick_links = [
        {
            "title": "Find a Team",
            "description": "Search and filter through all the teams",
            "url": "/teams/",
            "icon": "search",
        },
        {
            "title": "View Map",
            "description": "Explore hierarchies and dependencies",
            "url": "/organisation/",
            "icon": "organisation",
        },
        {
            "title": "Contact Teams",
            "description": "Quick access to team communication",
            "url": "/messages/",
            "icon": "messages",
        },
    ]

    return render(
        request,
        "users/user_dashboard.html",
        {
            "quick_links": quick_links,
            "recent_teams": recent_teams,
            "recent_updates": recent_updates,
        },
    )


@user_passes_test(is_admin_user, login_url="/login/")
def admin_dashboard(request):
    teams = list(
        Team.objects.select_related("department", "team_leader")
        .prefetch_related("users")
        .order_by("-team_id")[:2]
    )

    total_teams = Team.objects.count()
    active_projects = Project.objects.count()
    pending_issues = Team.objects.filter(team_leader__isnull=True).count()
    today = timezone.localdate()

    updates_today = (
        TeamMessage.objects.filter(created_at__date=today).count()
        + TeamMeeting.objects.filter(created_at__date=today).count()
    )

    audit_entries = AuditTrail.objects.select_related("admin_user").order_by("-created_at")[:5]

    team_rows = [
        {
            "name": team.team_name or f"Team {team.team_id}",
            "department": (
                team.department.department_name
                if team.department and team.department.department_name
                else "Unassigned"
            ),
            "lead": (
                team.team_leader.first_name
                or team.team_leader.username
                if team.team_leader
                else "-"
            ),
            "members": team.users.count(),
            "status": "On-Track" if team.project_count() else "Needs Planning",
        }
        for team in teams
    ]

    if not team_rows:
        team_rows = [
            {
                "name": "-",
                "department": "-",
                "lead": "-",
                "members": "-",
                "status": "-",
            }
        ]

    recent_activities = _build_admin_activities(limit=4)
    if not recent_activities:
        recent_activities = [{"title": "-", "display_time": "-"}]

    metric_cards = [
        {"label": "Total Teams", "value": _metric_value(total_teams)},
        {"label": "Active Projects", "value": _metric_value(active_projects)},
        {"label": "Pending Issues", "value": _metric_value(pending_issues)},
        {"label": "Updates Today", "value": _metric_value(updates_today)},
    ]

    return render(
        request,
        "users/admin_dashboard.html",
        {
            "metric_cards": metric_cards,
            "team_rows": team_rows,
            "recent_activities": recent_activities[:3],
            "audit_entries": audit_entries,
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
