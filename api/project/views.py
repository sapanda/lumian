"""
Views for the projects API.
"""
from rest_framework import (
    authentication,
    permissions,
    viewsets,
)

from .models import Project
from .serializers import ProjectSerializer


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

    def get_queryset(self):
        """Retrieve projects for authenticated user."""
        queryset = self.queryset
        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()