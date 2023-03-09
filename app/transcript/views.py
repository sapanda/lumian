"""
Views for the transcript API.
"""
from rest_framework import (
    viewsets,
    authentication,
    permissions,
    status,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from transcript.models import Transcript, AISynthesis, SynthesisType
from transcript.serializers import TranscriptSerializer, AISynthesisSerializer


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


class AISynthesisView(APIView):
    """"Base class for all AI synthesis views."""

    def get_of_type(self, request, pk, synthesis_type):
        """Retrieve the AISynthesis of the given type."""
        try:
            tct = Transcript.objects.get(pk=pk)  # noqa, needed for 404.
            synthesis = AISynthesis.objects.get(
                transcript=pk,
                output_type=synthesis_type
            )
            serializer = AISynthesisSerializer(synthesis)
            response = Response(serializer.data)
        except Transcript.DoesNotExist:
            response = Response(status=status.HTTP_404_NOT_FOUND)
        except AISynthesis.DoesNotExist:
            # TODO: Have a way to check if summary in progress
            response = Response(status=status.HTTP_202_ACCEPTED)

        return response


class SummaryView(AISynthesisView):
    """View for getting summary of a transcript."""
    def get(self, request, pk):
        return self.get_of_type(request, pk, SynthesisType.SUMMARY)


class ConciseView(AISynthesisView):
    """View for getting concise transcript."""
    def get(self, request, pk):
        return self.get_of_type(request, pk, SynthesisType.CONCISE)
