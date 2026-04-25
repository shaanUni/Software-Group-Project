# Authors: w2072520, w2112281

from django.urls import path
from . import views

# This 'app_name' provides the namespace (e.g., 'messaging:message-list')
app_name = 'scheduling'

urlpatterns = [
    path("", views.team_schedule, name="team-schedule"),
    path("create/", views.create_meeting, name="meeting-create"),
    path("<int:pk>/", views.meeting_detail, name="meeting-detail"),
]