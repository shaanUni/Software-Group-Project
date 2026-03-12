from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Team


@login_required
def team_list(request):
    teams = Team.objects.select_related("department", "meeting", "channel").all()
    return render(request, "teams/list.html", {"teams": teams})