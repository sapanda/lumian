"""
Utility functions for testing the meetingbot app.
"""
from django.contrib.auth import get_user_model
from meetingbot.models import MeetingBot


def create_user():
    """Create and return a new user."""
    return get_user_model().objects.create_user(
        name='testuser',
        email='testuser@example.com',
        password='testpass'
    )


def create_bot(user):
    """Create and return a new meeting bot."""
    return MeetingBot.objects.create(
        id='testbot',
        status=MeetingBot.StatusChoices.READY,
        message="",
        transcript=None,
        user=user
    )
