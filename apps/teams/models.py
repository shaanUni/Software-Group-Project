from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError

class Department(models.Model):
    department_id = models.AutoField(primary_key=True)
    department_name = models.TextField(blank=True, null=True)
    department_head = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="department_head",
        related_name="headed_departments",
    )

    class Meta:
        db_table = "department"

    def employee_count(self):
        return self.teams.aggregate(total=models.Count("users"))["total"] or 0

    def __str__(self):
        return self.department_name or f"Department {self.department_id}"


class Team(models.Model):
    team_id = models.AutoField(primary_key=True)
    team_name = models.TextField(blank=True, null=True)
    team_leader = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="team_leader",
        related_name="led_teams",
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        db_column="department_id",
        related_name="teams",
    )
    slack_channels = models.TextField(blank=True, null=True)
    daily_standup_time = models.TextField(blank=True, null=True)
    team_wiki = models.TextField(blank=True, null=True)
    development_focus_areas = models.TextField(blank=True, null=True)
    key_skills_technologies = models.TextField(blank=True, null=True)

    downstream_dependency = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="upstream_teams",
    )

    class Meta:
        db_table = "team"

    def employee_count(self):
        return self.users.count()

    def project_count(self):
        return self.projects.count()
    
    def clean(self):
        if self.downstream_dependency and self.downstream_dependency_id == self.team_id:
            raise ValidationError("A team cannot depend on itself.")

    def codebase_projects(self):
        return self.projects.exclude(codebase__isnull=True).exclude(codebase__exact="")

    def __str__(self):
        return self.team_name or f"Team {self.team_id}"


class User(AbstractUser):
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        db_column="team_id",
        related_name="users",
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "user"

    def __str__(self):
        full_name = self.get_full_name()
        return full_name or self.username


class Project(models.Model):
    project_id = models.AutoField(primary_key=True)
    project_name = models.TextField(blank=True, null=True)
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        db_column="team_id",
        related_name="projects",
    )
    codebase = models.TextField(blank=True, null=True)
    jira_link = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "project"

    def __str__(self):
        return self.project_name or f"Project {self.project_id}"