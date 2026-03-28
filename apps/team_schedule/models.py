from django.conf import settings
from django.db import models


class TeamMeeting(models.Model):
    meeting_id = models.AutoField(primary_key=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_team_meetings",
    )

    team_one = models.ForeignKey(
        "teams.Team",
        on_delete=models.CASCADE,
        related_name="meetings_as_team_one",
    )
    team_two = models.ForeignKey(
        "teams.Team",
        on_delete=models.CASCADE,
        related_name="meetings_as_team_two",
    )

    title = models.CharField(max_length=200)
    meeting_date = models.DateField()
    meeting_time = models.TimeField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "team_meeting"
        ordering = ["meeting_date", "meeting_time"]

    def __str__(self):
        return f"{self.title} - {self.team_one} / {self.team_two} on {self.meeting_date}"

    def other_team(self, current_team):
        if current_team == self.team_one:
            return self.team_two
        return self.team_one