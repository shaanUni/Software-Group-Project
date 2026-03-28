from django.contrib import admin
from .models import TeamMeeting


@admin.register(TeamMeeting)
class TeamMeetingAdmin(admin.ModelAdmin):
    list_display = (
        "meeting_id",
        "title",
        "team_one",
        "team_two",
        "meeting_date",
        "meeting_time",
        "created_by",
    )
    search_fields = ("title", "notes")
    list_filter = ("meeting_date", "team_one", "team_two")