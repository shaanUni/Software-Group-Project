from django.urls import path
from .views import team_list, superadmin_team_create, employee_create_view, team_edit_view

urlpatterns = [
    path("teams/", team_list, name="team-list"),
    path("teams/superadmin/add/", superadmin_team_create, name="superadmin-team-create"),
    path("teams/<int:pk>/edit/", team_edit_view, name="team-edit"),
    path("employees/add/", employee_create_view, name="employee-create"),
]