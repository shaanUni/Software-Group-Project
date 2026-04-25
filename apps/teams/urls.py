from django.urls import path
from .views import (
    team_list,
    superadmin_team_create,
    user_create_view,
    team_edit_view,
    organisation_view,
    team_detail,
    department_create_view,
    project_create_view,
)

urlpatterns = [
    path("teams/", team_list, name="team-list"),
    path("teams/create/", superadmin_team_create, name="team-create"),
    path("teams/<int:team_id>/", team_detail, name="team-detail"),
    path("teams/<int:pk>/edit/", team_edit_view, name="team-edit"),
    path("users/create/", user_create_view, name="user-create"),
    path("organisation/", organisation_view, name="organisation"),
    path("departments/create/", department_create_view, name="department-create"),
    path("projects/create/", project_create_view, name="project-create"),
]