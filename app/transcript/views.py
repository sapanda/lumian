"""
Views for the transcript API.
"""
from rest_framework import generics, authentication, permissions

from transcript.serializers import (
    TranscriptSerializer,
)


class CreateTranscriptView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = TranscriptSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """Create a new transcript."""
        serializer.save(user=self.request.user)
