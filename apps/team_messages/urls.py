from django.urls import path
from .views import message_list, message_create, message_detail

urlpatterns = [
    path("messages/", message_list, name="message-list"),
    path("messages/create/", message_create, name="message-create"),
    path("messages/create/<int:team_id>/", message_create, name="message-create-for-team"),
    path("messages/<int:pk>/", message_detail, name="message-detail"),
]