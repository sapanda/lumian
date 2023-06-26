"""
Serializers for the project API View.
"""
from rest_framework import serializers

from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for the project object."""

    transcript_count = serializers.CharField(read_only=True)
    start_time_min = serializers.CharField(read_only=True)
    end_time_max = serializers.CharField(read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'title', 'goal', 'questions', 'transcript_count',
                  'start_time_min', 'end_time_max']

    def create(self, validated_data):
        """Create and return a project."""
        return Project.objects.create(**validated_data)
