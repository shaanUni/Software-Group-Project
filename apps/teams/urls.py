from django.urls import path
from .views import team_list, superadmin_team_create

urlpatterns = [
    path("teams/", team_list, name="team-list"),
    path("teams/superadmin/add/", superadmin_team_create, name="superadmin-team-create"),
]