from django.urls import path
from . import views

urlpatterns = [
    path("teams/", views.team_list, name="team-list"),
]