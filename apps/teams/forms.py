from django import forms
from .models import Team


class TeamCreateForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = [
            "team_name",
            "team_leader",
            "department",
            "slack_channels",
            "daily_standup_time",
            "team_wiki",
            "development_focus_areas",
            "key_skills_technologies",
        ]
        widgets = {
            "team_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter team name"
            }),
            "team_leader": forms.Select(attrs={
                "class": "form-select"
            }),
            "department": forms.Select(attrs={
                "class": "form-select"
            }),
            "slack_channels": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "e.g. #frontend-team, #engineering"
            }),
            "daily_standup_time": forms.TimeInput(attrs={
                "class": "form-control",
                "type": "time"
            }),
            "team_wiki": forms.URLInput(attrs={
                "class": "form-control",
                "placeholder": "https://..."
            }),
            "development_focus_areas": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Describe the team's focus areas"
            }),
            "key_skills_technologies": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "List skills and technologies"
            }),
        }