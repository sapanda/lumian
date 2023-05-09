"""
Serializers for the project API View.
"""
from rest_framework import serializers

from .models import Project
from transcript.models import Transcript
from transcript.serializers import TranscriptSerializer


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for the project object."""

    transcripts = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'title', 'questions', 'transcripts']

    def get_transcripts(self, obj) -> list[dict]:
        transcripts = Transcript.objects.filter(project=obj)
        return [
            {
                'id': transcript.id,
                'title': transcript.title,
                'interviewees': transcript.interviewee_names,
                'interviewers': transcript.interviewer_names,
            }
            for transcript in transcripts
        ]

    def create(self, validated_data):
        """Create and return a project."""
        return Project.objects.create(**validated_data)
