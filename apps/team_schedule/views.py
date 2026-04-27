# Authors: w2072520, w2112281

import calendar
from datetime import date, datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q

from apps.team_messages.models import TeamMessage
from .forms import TeamMeetingForm
from .models import TeamMeeting


@login_required
def team_schedule(request):
    if not request.user.team:
        messages.error(request, "You are not assigned to a team.")
        return redirect("team-list")

    current_team = request.user.team

    today = date.today()
    year = request.GET.get("year")
    month = request.GET.get("month")

    try:
        year = int(year) if year else today.year
        month = int(month) if month else today.month
    except ValueError:
        year = today.year
        month = today.month

    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdatescalendar(year, month)

    # Improving how we fetch meetings to avoid loading too much data making site slow
    meetings = TeamMeeting.objects.select_related("team_one", "team_two").filter(
        Q(team_one=current_team) | Q(team_two=current_team),
        meeting_date__year=year,
        meeting_date__month=month,
    )

    # Upcoming meetings list, only show 5 meetings
    upcoming_meetings = TeamMeeting.objects.select_related("team_one", "team_two").filter(
        Q(team_one=current_team) | Q(team_two=current_team),
        meeting_date__gte=date.today()
    ).order_by('meeting_date', 'meeting_time')[:5]

    team_meetings = [
        meeting for meeting in meetings
        if meeting.team_one == current_team or meeting.team_two == current_team
    ]

    meetings_by_day = {}
    for meeting in team_meetings:
        meetings_by_day.setdefault(meeting.meeting_date, []).append(meeting)

    prev_month = month - 1
    prev_year = year
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1

    next_month = month + 1
    next_year = year
    if next_month == 13:
        next_month = 1
        next_year += 1

    context = {
        "current_team": current_team,
        "month_days": month_days,
        "meetings_by_day": meetings_by_day,
        "display_month": date(year, month, 1),
        "prev_month": prev_month,
        "prev_year": prev_year,
        "next_month": next_month,
        "next_year": next_year,
        "today": today,
        "upcoming_meetings": upcoming_meetings,
    }
    return render(request, "team_schedule/calendar.html", context)


@login_required
def create_meeting(request):
    if not request.user.team:
        messages.error(request, "You are not assigned to a team.")
        return redirect("team-list")

    current_team = request.user.team
    initial = {}

    selected_date = request.GET.get("date")
    if selected_date:
        initial["meeting_date"] = selected_date

    if request.method == "POST":
        form = TeamMeetingForm(request.POST, current_team=current_team)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.created_by = request.user
            meeting.team_one = current_team
            meeting.save()

            TeamMessage.objects.create(
                sender_team=current_team,
                recipient_team=meeting.team_two,
                sent_by=request.user,
                subject=f"New meeting scheduled: {meeting.title}",
                body=(
                    f"{current_team.team_name} scheduled a meeting with your team.\n\n"
                    f"Title: {meeting.title}\n"
                    f"Date: {meeting.meeting_date}\n"
                    f"Time: {meeting.meeting_time}\n\n"
                    f"Notes:\n{meeting.notes or 'No additional notes.'}"
                ),
            )

            messages.success(request, "Meeting scheduled successfully.")
            return redirect("scheduling:team-schedule")
    else:
        form = TeamMeetingForm(current_team=current_team, initial=initial)

    return render(
        request,
        "team_schedule/create.html",
        {
            "form": form,
            "current_team": current_team,
        },
    )


@login_required
def meeting_detail(request, pk):
    if not request.user.team:
        messages.error(request, "You are not assigned to a team.")
        return redirect("team-list")

    current_team = request.user.team

    meeting = get_object_or_404(
        TeamMeeting.objects.select_related("team_one", "team_two", "created_by"),
        pk=pk,
    )

    if meeting.team_one != current_team and meeting.team_two != current_team:
        messages.error(request, "You do not have permission to view this meeting.")
        return redirect("scheduling:team-schedule")

    return render(
        request,
        "team_schedule/detail.html",
        {
            "meeting": meeting,
            "current_team": current_team,
        },
    )