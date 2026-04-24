# Authors: w2072520, w2112281

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import TeamMessageForm
from .models import TeamMessage
from apps.teams.models import Team


# Message inbox
@login_required
def message_list(request):
    if not request.user.team:
        messages.error(request, "You are not assigned to a team.")
        return redirect("team-list")

    current_team = request.user.team

    inbox = TeamMessage.objects.select_related(
        "sender_team", "recipient_team", "sent_by"
    ).filter(recipient_team=current_team)

    sent = TeamMessage.objects.select_related(
        "sender_team", "recipient_team", "sent_by"
    ).filter(sender_team=current_team)

    return render(
        request,
        "team_messages/list.html",
        {
            "current_team": current_team,
            "inbox": inbox,
            "sent": sent,
        },
    )

# Messages sent
@login_required
def message_sent(request):
    if not request.user.team:
        messages.error(request, "You are not assigned to a team.")
        return redirect("team-list")

    current_team = request.user.team

    sent = TeamMessage.objects.select_related(
        "sender_team", "recipient_team", "sent_by"
    ).filter(sender_team=current_team)


    return render(
        request,
        "team_messages/sent.html",
        {
            "current_team": current_team,
            "sent": sent,
        },
    )


@login_required
def message_create(request, team_id=None):
    if not request.user.team:
        messages.error(request, "You are not assigned to a team.")
        return redirect("team-list")

    sender_team = request.user.team
    initial = {}

    if team_id is not None:
        recipient_team = get_object_or_404(Team, pk=team_id)

        if recipient_team == sender_team:
            messages.error(request, "You cannot send a message to your own team.")
            return redirect("team-list")

        initial["recipient_team"] = recipient_team

    if request.method == "POST":
        form = TeamMessageForm(request.POST, sender_team=sender_team)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender_team = sender_team
            message.sent_by = request.user
            message.save()
            messages.success(request, "Message sent successfully.")
            return redirect("message-list")
    else:
        form = TeamMessageForm(sender_team=sender_team, initial=initial)

    return render(
        request,
        "team_messages/create.html",
        {
            "form": form,
            "sender_team": sender_team,
        },
    )


@login_required
def message_detail(request, pk):
    if not request.user.team:
        messages.error(request, "You are not assigned to a team.")
        return redirect("team-list")

    current_team = request.user.team

    message = get_object_or_404(
        TeamMessage.objects.select_related("sender_team", "recipient_team", "sent_by"),
        pk=pk,
    )

    if message.sender_team != current_team and message.recipient_team != current_team:
        messages.error(request, "You do not have permission to view this message.")
        return redirect("message-list")

    return render(
        request,
        "team_messages/detail.html",
        {
            "message": message,
            "current_team": current_team,
        },
    )