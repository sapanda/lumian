"""
Serializers for the transcript API View.
"""
from rest_framework import serializers

from transcript.models import Transcript, AISynthesis, Query


class TranscriptSerializer(serializers.ModelSerializer):
    """Serializer for the transcript object."""

    class Meta:
        model = Transcript
        fields = ['id', 'title', 'interviewee_names',
                  'interviewer_names', 'transcript']

    def create(self, validated_data):
        """Create and return a transcript."""
        return Transcript.objects.create(**validated_data)


class AISynthesisSerializer(serializers.ModelSerializer):
    """Serializer for the AISynthesis object."""
    class Meta:
        model = AISynthesis
        fields = ['output']

    def create(self, validated_data):
        """Create and return a transcript summary."""
        return AISynthesis.objects.create(**validated_data)


class QuerySerializer(serializers.ModelSerializer):
    """Serializer for the Transcript Query object."""
    class Meta:
        model = Query
        fields = ['id', 'query', 'result']

    def create(self, validated_data):
        """Create and return a Transcript Query."""
        return Query.objects.create(**validated_data)
