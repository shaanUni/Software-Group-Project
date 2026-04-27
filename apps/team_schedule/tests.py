# Author: w2112281

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.teams.models import Team, Department
from apps.team_messages.models import TeamMessage
from .models import TeamMeeting
from datetime import date, time

User = get_user_model()

class TeamScheduleTests(TestCase):
    def setUp(self):

        # Setup department using Department model
        self.dept = Department.objects.create(department_name="xTV_Web")

        # Setup teams using Team model
        self.team_a = Team.objects.create(team_name="Code Warriors", department=self.dept)
        self.team_b = Team.objects.create(team_name="The Debuggers", department=self.dept)
        self.team_c = Team.objects.create(team_name="Bit Masters", department=self.dept)

        # Setup users using User Model with team affiliations
        self.user_a = User.objects.create_user(username="OliviaCarter", password="password123")
        self.user_a.team = self.team_a
        self.user_a.save()

        self.user_b = User.objects.create_user(username="JamesBennett", password="password123")
        self.user_b.team = self.team_b
        self.user_b.save()

        # Initialize Client
        self.client = Client()

    def test_calendar_filtering(self):
        """Test that only meetings involving the user's team appear in the schedule."""
        # Meeting for Olivia's team
        TeamMeeting.objects.create(
            title="The Debuggers Meeting",
            created_by=self.user_a,
            team_one=self.team_a,
            team_two=self.team_b,
            meeting_date=date.today(),
            meeting_time=time(10, 0)
        )
        # Meeting Olivia shouldn't see
        TeamMeeting.objects.create(
            title="Bit Masters Meeting",
            created_by=self.user_a,
            team_one=self.team_b,
            team_two=self.team_c,
            meeting_date=date.today(),
            meeting_time=time(11, 0)
        )

        self.client.login(username="OliviaCarter", password="password123")
        response = self.client.get(reverse('scheduling:team-schedule'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The Debuggers Meeting")
        self.assertNotContains(response, "Bit Masters Meeting")

    def test_meeting_detail_privacy(self):
        """Ensure users can't view details of meetings they aren't part of."""
        private_meeting = TeamMeeting.objects.create(
            title="Private Discussion",
            created_by=self.user_a,
            team_one=self.team_b,
            team_two=self.team_c,
            meeting_date=date.today(),
            meeting_time=time(14, 0)
        )

        self.client.login(username="OliviaCarter", password="password123")
        response = self.client.get(reverse('scheduling:meeting-detail', kwargs={'pk': private_meeting.pk}), follow=True)

        self.assertContains(response, "You do not have permission to view this meeting.")

    def test_create_meeting_sends_notification(self):
        """INTEGRATION TEST: Creating a meeting must trigger a TeamMessage."""
        self.client.login(username="OliviaCarter", password="password123")

        post_data = {
            'team_two': self.team_b.pk,
            'title': 'Sync Meeting',
            'meeting_date': date.today(),
            'meeting_time': '15:00',
            'notes': 'Discussion about the API'
        }

        # Submitting the meeting creation form
        self.client.post(reverse('scheduling:meeting-create'), data=post_data)

        # Checking if the meeting was created
        self.assertEqual(TeamMeeting.objects.count(), 1)

        # Check if the notification message was sent to Team B
        notification = TeamMessage.objects.filter(recipient_team=self.team_b).first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.sender_team, self.team_a)
        self.assertIn("New meeting scheduled: Sync Meeting", notification.subject)

    def test_upcoming_meetings_logic(self):
        """Test that the 'upcoming_meetings' list only shows future/today meetings."""
        # Creating a meeting in the future
        TeamMeeting.objects.create(
            title="Future meeting",
            created_by=self.user_a,
            team_one=self.team_a,
            team_two=self.team_b,
            meeting_date=date(2026, 12, 31),
            meeting_time=time(10, 0)
        )

        self.client.login(username="OliviaCarter", password="password123")
        response = self.client.get(reverse('scheduling:team-schedule'))

        self.assertIn('upcoming_meetings', response.context)
        self.assertTrue(any(m.title == "Future meeting" for m in response.context['upcoming_meetings']))