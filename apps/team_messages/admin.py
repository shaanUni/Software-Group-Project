from django.contrib import admin
from .models import TeamMessage


@admin.register(TeamMessage)
class TeamMessageAdmin(admin.ModelAdmin):
    list_display = (
        "message_id",
        "sender_team",
        "recipient_team",
        "sent_by",
        "subject",
        "created_at",
    )
    search_fields = ("subject", "body")
    list_filter = ("sender_team", "recipient_team", "created_at")