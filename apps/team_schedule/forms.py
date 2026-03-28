from django import forms
from apps.teams.models import Team
from .models import TeamMeeting


class TeamMeetingForm(forms.ModelForm):
    class Meta:
        model = TeamMeeting
        fields = ["team_two", "title", "meeting_date", "meeting_time", "notes"]
        widgets = {
            "team_two": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Meeting title"
            }),
            "meeting_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),
            "meeting_time": forms.TimeInput(attrs={
                "class": "form-control",
                "type": "time"
            }),
            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Optional notes"
            }),
        }

    def __init__(self, *args, **kwargs):
        current_team = kwargs.pop("current_team", None)
        super().__init__(*args, **kwargs)

        if current_team:
            self.fields["team_two"].queryset = Team.objects.exclude(pk=current_team.pk)