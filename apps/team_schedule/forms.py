# Authors: w2072520, w2112281

from django import forms
from apps.teams.models import Team
from .models import TeamMeeting
from datetime import date


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

    # Adding a minimum date to the HTML calendar picker,
    # to prevent scheduling meetings in the past
    def __init__(self, *args, **kwargs):
        current_team = kwargs.pop("current_team", None)
        super().__init__(*args, **kwargs)

        # Set the minimum date in the HTML calendar picker to today
        today = date.today().isoformat()
        self.fields['meeting_date'].widget.attrs['min'] = today

        if current_team:
            self.fields["team_two"].queryset = Team.objects.exclude(pk=current_team.pk)

    def clean_meeting_date(self):
        meeting_date = self.cleaned_data.get('meeting_date')
        if meeting_date and meeting_date < date.today():
            raise forms.ValidationError("The meeting date cannot be in the past!")
        return meeting_date