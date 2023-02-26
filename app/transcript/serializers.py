"""
Serializers for the transcript API View.
"""
from rest_framework import serializers

from transcript.models import Transcript


class TranscriptSerializer(serializers.ModelSerializer):
    """Serializer for the transcript object."""

    class Meta:
        model = Transcript
        fields = ['id', 'title', 'interviewee_names',
                  'interviewer_names', 'transcript']
        read_only_fields = ['id']

    def create(self, validated_data):
        """Create and return a transcript."""
        return Transcript.objects.create(**validated_data)
