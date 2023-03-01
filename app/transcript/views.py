"""
Views for the transcript API.
"""
from rest_framework import (
    viewsets,
    authentication,
    permissions,
)

from transcript.models import Transcript
from transcript.serializers import TranscriptSerializer


class TranscriptView(viewsets.ModelViewSet):
    """View for managing Transcript APIs."""
    serializer_class = TranscriptSerializer
    queryset = Transcript.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """Create a new transcript."""
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """Retrieve transcripts for authenticated user."""
        queryset = self.queryset
        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()
