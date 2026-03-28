from django.conf import settings
from django.db import models


class TeamMessage(models.Model):
    message_id = models.AutoField(primary_key=True)

    sender_team = models.ForeignKey(
        "teams.Team",
        on_delete=models.CASCADE,
        related_name="sent_team_messages",
    )
    recipient_team = models.ForeignKey(
        "teams.Team",
        on_delete=models.CASCADE,
        related_name="received_team_messages",
    )
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_team_messages",
    )

    subject = models.CharField(max_length=200)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "team_message"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.sender_team} -> {self.recipient_team}: {self.subject}"