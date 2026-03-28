from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Department, Team, User, Project


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Organisation", {"fields": ("team",)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Organisation", {"fields": ("team",)}),
    )


admin.site.register(Department)
admin.site.register(Team)
admin.site.register(Project)