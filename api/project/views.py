"""
Views for the projects API.
"""
from rest_framework import (
    authentication,
    permissions,
    viewsets,
)
from rest_framework.response import Response
from django.db.models import Count, Min, Max
from .models import Project
from .serializers import (
    ProjectSerializer,
    ProjectListSerializer
)

import logging
logger = logging.getLogger(__name__)


class ProjectView(viewsets.ModelViewSet):
    """View for managing Project APIs."""
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'head', 'delete']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        else:
            return ProjectSerializer

    def perform_create(self, serializer):
        """Create a new project."""
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """Retrieve projects for authenticated user."""
        queryset = self.queryset
        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Annotate the count of transcripts for each project
        queryset = queryset.annotate(transcript_count=Count('transcript'))
        queryset = queryset.annotate(start_time=Min('transcript__start_time'),
                                     end_time=Max('transcript__end_time'))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
