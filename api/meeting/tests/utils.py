"""
Utility functions for testing the meetingbot app.
"""
from django.contrib.auth import get_user_model
from meeting.models import MeetingBot
from project.models import Project


def create_user():
    """Create and return a new user."""
    return get_user_model().objects.create_user(
        name='testuser',
        email='testuser@example.com',
        password='testpass',
        bot_name='LumianBot'
    )


def create_project(user):
    return Project.objects.create(
        user=user,
        title='Test Project',
        goal='Test',
        questions=['Test']
    )


def create_bot(project):
    """Create and return a new meeting bot."""
    return MeetingBot.objects.create(
        id='testbot',
        status=MeetingBot.StatusChoices.READY,
        message="",
        transcript=None,
        project=project
    )
