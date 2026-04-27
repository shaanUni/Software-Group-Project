# Author: w2112281

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.teams.models import Team
from apps.teams.models import Department
from .models import TeamMessage

User = get_user_model()

class TeamMessagingTests(TestCase):
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

    def test_inbox_filtering(self):
        """Ensure users only see messages sent to THEIR team in the inbox."""
        # Message for Team A
        TeamMessage.objects.create(
            sender_team=self.team_b,
            recipient_team=self.team_a,
            sent_by=self.user_b,
            subject="Hello Olivia",
            body="Good luck today"
        )
        # Message for Team C
        TeamMessage.objects.create(
            sender_team=self.team_b,
            recipient_team=self.team_c,
            sent_by=self.user_b,
            subject="Private",
            body="Secret Cinema stuff"
        )

        self.client.login(username="OliviaCarter", password="password123")
        response = self.client.get(reverse('messaging:message-list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello Olivia")
        self.assertNotContains(response, "Secret Cinema stuff")

    def test_message_detail_permission(self):
        """Prevent a user from viewing a message detail page that doesn't involve their team."""
        # Message between Team B and Team C
        private_msg = TeamMessage.objects.create(
            sender_team=self.team_b,
            recipient_team=self.team_c,
            sent_by=self.user_b,
            subject="Confidential",
            body="Top secret"
        )

        # OliviaCarter (Team A) tries to view it
        self.client.login(username="OliviaCarter", password="password123")
        response = self.client.get(
            reverse('messaging:message-detail', kwargs={'pk': private_msg.pk}),
            follow=True
        )

        # Checking that the user is redirected to the message list and sees an error message
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You do not have permission to view this message.")

    def test_send_message_to_own_team_fails(self):
        """Test that the view prevents sending a message to your own team."""
        self.client.login(username="OliviaCarter", password="password123")

        # Using the message-create-for-team URL with Olivia's own team ID
        response = self.client.get(reverse('messaging:message-create-for-team', kwargs={'team_id': self.team_a.pk}))

        self.assertRedirects(response, reverse('team-list'))

    def test_successful_message_creation(self):
        """Test the full flow of sending a message via POST."""
        self.client.login(username="OliviaCarter", password="password123")

        post_data = {
            'recipient_team': self.team_b.pk,
            'subject': 'Meeting Request',
            'body': 'Let us sync up at 5pm.'
        }

        response = self.client.post(reverse('messaging:message-create'), data=post_data)

        # Check if redirect happened (successful save)
        self.assertRedirects(response, reverse('messaging:message-list'))

        # Check database
        self.assertEqual(TeamMessage.objects.filter(subject='Meeting Request').count(), 1)
        msg = TeamMessage.objects.get(subject='Meeting Request')
        self.assertEqual(msg.sender_team, self.team_a)
        self.assertEqual(msg.sent_by, self.user_a)

    def test_unassigned_user_access(self):
        """Ensure users without a team are redirected as per your view logic."""
        homeless_user = User.objects.create_user(username="no_team", password="password123")
        self.client.login(username="no_team", password="password123")

        # Redirect to team list page
        response = self.client.get(reverse('messaging:message-list'))
        self.assertRedirects(response, reverse('team-list'))