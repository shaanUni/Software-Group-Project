from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("mockup_teams", views.mockup_teams, name="mockup_teams"),
    path("mockup_organisation", views.mockup_organisation, name="mockup_organisation")
]