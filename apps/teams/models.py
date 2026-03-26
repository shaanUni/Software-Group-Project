from django.db import models


class Department(models.Model):
    department_id = models.AutoField(primary_key=True)
    department_name = models.TextField(blank=True, null=True)
    department_head = models.ForeignKey(
        "Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="department_head",
        related_name="headed_departments",
    )

    class Meta:
        db_table = "department"

    def employee_count(self):
        return self.teams.aggregate(total=models.Count("employees"))["total"] or 0
    
    def __str__(self):
        return self.department_name or f"Department {self.department_id}"


class Team(models.Model):
    team_id = models.AutoField(primary_key=True)
    team_name = models.TextField(blank=True, null=True)
    team_leader = models.ForeignKey(
        "Employee",
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

    class Meta:
        db_table = "team"
    
    def employee_count(self):
        return self.employees.count()
    
    def project_count(self):
        return self.projects.count()
    
    def __str__(self):
        return self.team_name or f"Team {self.team_id}"


class Employee(models.Model):
    employee_id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        db_column="team_id",
        related_name="employees",
    )

    class Meta:
        db_table = "employee"

    def __str__(self):
        return self.name or f"Employee {self.employee_id}"


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