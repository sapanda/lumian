"""
Serializers for the transcript API View.
"""
from rest_framework import serializers

from transcript.models import Transcript, Synthesis, Query


class TranscriptSerializer(serializers.ModelSerializer):
    """Serializer for the transcript object."""

    class Meta:
        model = Transcript
        fields = ['id', 'project', 'title', 'interviewee_names',
                  'interviewer_names', 'transcript',
                  'start_time', 'end_time']

    def create(self, validated_data):
        """Create and return a transcript."""
        return Transcript.objects.create(**validated_data)


class SynthesisSerializer(serializers.ModelSerializer):
    """Serializer for the Synthesis object."""
    class Meta:
        model = Synthesis
        fields = ['output']

    def create(self, validated_data):
        """Create and return a transcript summary."""
        return Synthesis.objects.create(**validated_data)


class QuerySerializer(serializers.ModelSerializer):
    """Serializer for the Transcript Query object."""
    class Meta:
        model = Query
        fields = ['query', 'output']

    def create(self, validated_data):
        """Create and return a Transcript Query."""
        return Query.objects.create(**validated_data)
