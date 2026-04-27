from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
import csv

from .forms import RegisterForm, UserUpdateForm
from .forms import AdminUserCreateForm
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


def _supports_additional_teams(User):
    return any(field.name == "additional_teams" for field in User._meta.get_fields())


def _filtered_users_queryset(User, params):
    query = (params.get("q") or "").strip()
    role = (params.get("role") or "").strip()
    team = (params.get("team") or "").strip()
    status = (params.get("status") or "").strip()
    users = User.objects.select_related("team").order_by("username")

    if _supports_additional_teams(User):
        users = users.prefetch_related("additional_teams")

    if query:
        users = users.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
        )

    if role == "admin":
        users = users.filter(is_superuser=True)
    elif role == "staff":
        users = users.filter(is_staff=True, is_superuser=False)
    elif role == "member":
        users = users.filter(is_staff=False, is_superuser=False)

    if status == "active":
        users = users.filter(is_active=True)
    elif status == "inactive":
        users = users.filter(is_active=False)

    if team.isdigit():
        if _supports_additional_teams(User):
            users = users.filter(Q(team_id=int(team)) | Q(additional_teams__team_id=int(team))).distinct()
        else:
            users = users.filter(team_id=int(team))

    filters = {
        "q": query,
        "role": role,
        "team": team,
        "status": status,
    }
    return users, filters


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


@user_passes_test(is_admin_user, login_url="/login/")
def admin_user_management(request):
    User = get_user_model()
    has_additional_teams = _supports_additional_teams(User)
    teams = Team.objects.order_by("team_name", "team_id")
    create_form = AdminUserCreateForm(
        teams=teams,
        supports_additional_teams=has_additional_teams,
    )

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "create":
            if not request.user.is_superuser:
                messages.error(request, "Only superusers can create users.")
                return redirect("admin-user-management")

            create_form = AdminUserCreateForm(
                request.POST,
                teams=teams,
                supports_additional_teams=has_additional_teams,
            )

            if create_form.is_valid():
                new_user = create_form.save()
                messages.success(request, f"Created user {new_user.username}.")
                return redirect("admin-user-management")

            users_qs, filters = _filtered_users_queryset(User, request.GET)
            users = list(users_qs)
            for account in users:
                assigned = []
                if has_additional_teams:
                    assigned = list(account.additional_teams.all())
                if account.team and all(team.pk != account.team.pk for team in assigned):
                    assigned.insert(0, account.team)
                account.assigned_teams = assigned

            return render(
                request,
                "users/admin_user_management.html",
                {
                    "users": users,
                    "teams": teams,
                    "filters": filters,
                    "create_form": create_form,
                },
            )

        if action in {"bulk_deactivate", "bulk_assign", "export_csv"}:
            selected_ids = request.POST.getlist("selected_users")
            selected_users = User.objects.filter(pk__in=selected_ids)

            if action == "bulk_deactivate":
                if not selected_ids:
                    messages.error(request, "Select at least one user for bulk deactivate.")
                    return redirect("admin-user-management")

                deactivated_count = selected_users.exclude(pk=request.user.pk).update(is_active=False)
                if selected_users.filter(pk=request.user.pk).exists():
                    messages.warning(request, "Your own account was skipped for safety.")
                messages.success(request, f"Deactivated {deactivated_count} user(s).")
                return redirect("admin-user-management")

            if action == "bulk_assign":
                if not selected_ids:
                    messages.error(request, "Select at least one user for bulk assign.")
                    return redirect("admin-user-management")

                bulk_team_id = request.POST.get("bulk_team_id")
                team = Team.objects.filter(pk=bulk_team_id).first()
                if not team:
                    messages.error(request, "Choose a valid team for bulk assignment.")
                    return redirect("admin-user-management")

                for account in selected_users:
                    if has_additional_teams:
                        account.additional_teams.add(team)
                    if account.team_id is None or not has_additional_teams:
                        account.team = team
                        account.save(update_fields=["team"])

                messages.success(request, f"Assigned {selected_users.count()} user(s) to {team.team_name or f'Team {team.team_id}'}.")
                return redirect("admin-user-management")

            users_for_export = selected_users
            if not selected_ids:
                users_for_export, _ = _filtered_users_queryset(User, request.POST)

            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="user_list.csv"'
            writer = csv.writer(response)
            writer.writerow(["Username", "Name", "Email", "Role", "Active", "Team"])
            for account in users_for_export:
                if account.is_superuser:
                    role = "Superuser"
                elif account.is_staff:
                    role = "Staff"
                else:
                    role = "Member"
                writer.writerow(
                    [
                        account.username,
                        account.get_full_name() or account.username,
                        account.email,
                        role,
                        "yes" if account.is_active else "no",
                        account.team.team_name if account.team else "",
                    ]
                )
            return response

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
                if has_additional_teams:
                    target_user.additional_teams.clear()
                target_user.team = None
                target_user.save(update_fields=["team"])
                target_user.delete()
                messages.success(request, f"Deleted user {target_user.username}.")
            return redirect("admin-user-management")

        if action == "update":
            selected_team_ids = request.POST.getlist("team_ids")
            if not selected_team_ids:
                single_team_id = request.POST.get("team_id")
                if single_team_id:
                    selected_team_ids = [single_team_id]

            selected_teams_by_id = {
                str(team.pk): team for team in Team.objects.filter(pk__in=selected_team_ids)
            }
            selected_teams = [
                selected_teams_by_id[team_id]
                for team_id in selected_team_ids
                if team_id in selected_teams_by_id
            ]

            target_user.team = selected_teams[0] if selected_teams else None
            target_user.save(update_fields=["team"])
            if has_additional_teams:
                target_user.additional_teams.set(selected_teams)

            if request.user.is_superuser and request.headers.get("x-requested-with") != "XMLHttpRequest":
                if target_user.pk == request.user.pk:
                    target_user.is_staff = True
                    target_user.is_superuser = True
                    target_user.is_active = True
                else:
                    target_user.is_staff = request.POST.get("is_staff") == "on"
                    target_user.is_superuser = request.POST.get("is_superuser") == "on"
                    target_user.is_active = request.POST.get("is_active") == "on"
                target_user.save(update_fields=["is_staff", "is_superuser", "is_active"])

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "ok": True,
                        "teams": [
                            {"id": team.pk, "name": team.team_name or "Team"}
                            for team in selected_teams
                        ],
                    }
                )

            messages.success(request, f"Updated user {target_user.username}.")
            return redirect("admin-user-management")

        messages.error(request, "Unknown action requested.")
        return redirect("admin-user-management")

    users_qs, filters = _filtered_users_queryset(User, request.GET)
    users = list(users_qs)
    for account in users:
        assigned = []
        if has_additional_teams:
            assigned = list(account.additional_teams.all())
        if account.team and all(team.pk != account.team.pk for team in assigned):
            assigned.insert(0, account.team)
        account.assigned_teams = assigned

    return render(
        request,
        "users/admin_user_management.html",
        {
            "users": users,
            "teams": teams,
            "filters": filters,
            "create_form": create_form,
        },
    )


@user_passes_test(is_admin_user, login_url="/login/")
def admin_user_detail(request, user_id):
    User = get_user_model()
    account_qs = User.objects.select_related("team")
    if _supports_additional_teams(User):
        account_qs = account_qs.prefetch_related("additional_teams")
    account = get_object_or_404(account_qs, pk=user_id)

    teams = []
    if _supports_additional_teams(User):
        teams = list(account.additional_teams.all())
    if account.team and account.team not in teams:
        teams.insert(0, account.team)

    return render(
        request,
        "users/admin_user_detail.html",
        {
            "account": account,
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