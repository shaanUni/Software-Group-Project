from django.urls import path
from .views import team_schedule, create_meeting, meeting_detail

urlpatterns = [
    path("schedule/", team_schedule, name="team-schedule"),
    path("schedule/create/", create_meeting, name="meeting-create"),
    path("schedule/<int:pk>/", meeting_detail, name="meeting-detail"),
]