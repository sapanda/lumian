"""
Serializers for the project API View.
"""
from rest_framework import serializers

from .models import Project
from transcript.models import Transcript


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for the project object."""

    class Meta:
        model = Project
        fields = ['id', 'title', 'questions']

    def create(self, validated_data):
        """Create and return a project."""
        return Project.objects.create(**validated_data)
