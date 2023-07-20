"""
Serializers for the transcript API View.
"""
from rest_framework import serializers
from transcript.models import Transcript, Synthesis, Query
from meeting.external_clients.assembly import get_transcription_for_audio


class TranscriptFileField(serializers.FileField):
    def to_internal_value(self, data):
        """
        Handle the file upload and read its content.
        """
        file_obj = super().to_internal_value(data)

        # Read the content of the file and convert it to a string
        if file_obj:
            content_type = file_obj.content_type
            if content_type == 'text/plain':
                transcript_content = file_obj.read().decode('utf-8')
            elif content_type == 'audio/mpeg':
                transcript_content = get_transcription_for_audio(file_obj)
            else:
                raise serializers.ValidationError(
                    'Invalid file format. Only .txt/.mp3 files are allowed.')

            return transcript_content

        return None


class TranscriptSerializer(serializers.ModelSerializer):
    """Serializer for the transcript object."""

    file = TranscriptFileField(write_only=True)
    transcript = serializers.CharField(read_only=True)

    class Meta:
        model = Transcript
        fields = ['id', 'project', 'title', 'interviewee_names',
                  'interviewer_names', 'file', 'transcript',
                  'start_time', 'end_time']

    def create(self, validated_data):
        file = validated_data.pop('file', None)

        # Process the file and get the transcript text
        if file:
            transcript_text = file
        else:
            transcript_text = ''

        # Create the YourModel record in the database
        data = {'transcript': transcript_text, **validated_data}
        return Transcript.objects.create(**data)


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
