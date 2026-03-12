from django.db import models


class Department(models.Model):
    department_id = models.AutoField(primary_key=True)
    department_name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_date = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "department"

    def __str__(self):
        return self.department_name or f"Department {self.department_id}"


class ContactChannel(models.Model):
    channel_id = models.AutoField(primary_key=True)
    channel_type = models.TextField(blank=True, null=True)
    channel_value = models.TextField(blank=True, null=True)
    is_primary = models.IntegerField(default=0)

    class Meta:
        db_table = "contact_channel"

    def __str__(self):
        return self.channel_value or f"Channel {self.channel_id}"


class MeetingSchedule(models.Model):
    meeting_id = models.AutoField(primary_key=True)
    title = models.TextField(blank=True, null=True)
    duration_minutes = models.IntegerField(blank=True, null=True)
    platform = models.TextField(blank=True, null=True)
    frequency = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    scheduled_date = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "meeting_schedule"

    def __str__(self):
        return self.title or f"Meeting {self.meeting_id}"


class Team(models.Model):
    team_id = models.AutoField(primary_key=True)
    team_name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    mission_statement = models.TextField(blank=True, null=True)
    created_date = models.TextField(blank=True, null=True)
    is_active = models.IntegerField(default=0)
    slack_channels = models.TextField(blank=True, null=True)
    daily_startup_time = models.TextField(blank=True, null=True)
    team_wiki = models.TextField(blank=True, null=True)
    development_focus_areas = models.TextField(blank=True, null=True)
    key_skills_technologies = models.TextField(blank=True, null=True)
    dependency_id = models.IntegerField()
    dependency_type = models.TextField(blank=True, null=True)
    dependency_description = models.TextField(blank=True, null=True)

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        db_column="department_id",
        related_name="teams",
    )
    meeting = models.ForeignKey(
        MeetingSchedule,
        on_delete=models.CASCADE,
        db_column="meeting_id",
        related_name="teams",
    )
    channel = models.ForeignKey(
        ContactChannel,
        on_delete=models.CASCADE,
        db_column="channel_id",
        related_name="teams",
    )

    class Meta:
        db_table = "team"

    def __str__(self):
        return self.team_name or f"Team {self.team_id}"


class CodeRepository(models.Model):
    repo_id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    url = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    created_date = models.TextField(blank=True, null=True)

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        db_column="team_id",
        related_name="repositories",
    )

    class Meta:
        db_table = "codeRepository"

    def __str__(self):
        return self.name or f"Repo {self.repo_id}"