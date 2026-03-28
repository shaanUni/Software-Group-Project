from django import forms
from .models import TeamMessage
from apps.teams.models import Team


class TeamMessageForm(forms.ModelForm):
    class Meta:
        model = TeamMessage
        fields = ["recipient_team", "subject", "body"]
        widgets = {
            "recipient_team": forms.Select(attrs={"class": "form-select"}),
            "subject": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter subject"}
            ),
            "body": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": "Write your message here",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        sender_team = kwargs.pop("sender_team", None)
        super().__init__(*args, **kwargs)

        if sender_team:
            self.fields["recipient_team"].queryset = Team.objects.exclude(
                pk=sender_team.pk
            )