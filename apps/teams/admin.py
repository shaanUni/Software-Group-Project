from django.contrib import admin
from .models import Department, Team, Employee, Project

admin.site.register(Department)
admin.site.register(Team)
admin.site.register(Employee)
admin.site.register(Project)