from django.contrib import admin
from .models import Department, ContactChannel, MeetingSchedule, Team, CodeRepository

admin.site.register(Department)
admin.site.register(ContactChannel)
admin.site.register(MeetingSchedule)
admin.site.register(Team)
admin.site.register(CodeRepository)