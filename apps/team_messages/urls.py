from django.urls import path
from . import views

# This 'app_name' provides the namespace (e.g., 'messaging:message-list')
app_name = 'messaging'

urlpatterns = [
    path("", views.message_list, name="message-list"),
    path("create/", views.message_create, name="message-create"),
    path("sent/", views.message_sent, name="message-sent"),
    path("create/<int:team_id>/", views.message_create, name="message-create-for-team"),
    path("<int:pk>/", views.message_detail, name="message-detail"),
]