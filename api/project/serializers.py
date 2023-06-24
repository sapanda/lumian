"""
Serializers for the project API View.
"""
from rest_framework import serializers

from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for the project object."""

    class Meta:
        model = Project
        fields = ['id', 'title', 'goal', 'questions']

    def create(self, validated_data):
        """Create and return a project."""
        return Project.objects.create(**validated_data)


class ProjectListSerializer(serializers.ModelSerializer):
    """Serializer for the project object."""

    transcript_count = serializers.CharField()
    start_time = serializers.CharField()
    end_time = serializers.CharField()

    class Meta:
        model = Project
        fields = ['id', 'title', 'goal', 'questions',
                  'transcript_count', 'start_time', 'end_time']

    def create(self, validated_data):
        """Create and return a project."""
        return Project.objects.create(**validated_data)
