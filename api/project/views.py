"""
Views for the projects API.
"""
from rest_framework import (
    authentication,
    permissions,
    viewsets,
    status
)
from rest_framework.response import Response
from django.db.models import Count, Min, Max
from .models import Project
from .serializers import (
    ProjectSerializer
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

    def perform_create(self, serializer):
        """Create a new project."""
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        instance = super().create(request, *args, **kwargs)
        return Response({'data': instance.data,
                         'message': 'Project Created'},
                        status.HTTP_201_CREATED)

    def get_queryset(self):
        """Retrieve projects for authenticated user."""
        queryset = self.queryset
        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset:
            # Annotate the count of transcripts for each project
            queryset = queryset.annotate(transcript_count=Count('transcript'))
            queryset = queryset.annotate(
                start_time_min=Min('transcript__start_time'),
                end_time_max=Max('transcript__end_time'))
            data = self.get_serializer(queryset, many=True).data
            message = ""
        else:
            data = {}
            message = 'No projects found'
        return Response({'data': data, 'message': message})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        message = "Project deleted successfully"
        return Response({'message': message}, status=status.HTTP_200_OK)
