"""
Serializers for the transcript API View.
"""
from rest_framework import serializers
from transcript.models import Transcript, Synthesis, Query
from meeting.external_clients.assembly import get_transcription_for_audio
from transcript.utils import (
    pre_process_transcript,
    is_valid_transcript_format
)


class TranscriptFileField(serializers.FileField):
    def to_internal_value(self, data):
        """
        Handle the file upload and read its content.
        """
        file_obj = super().to_internal_value(data)
        supported_audio_formats = ['mpeg', 'wav', 'ogg', 'flac', 'mp4']
        audio_content_types = ['audio/' + format
                               for format in supported_audio_formats]

        # Read the content of the file and convert it to a string
        if file_obj:
            content_type = file_obj.content_type
            # for text files
            if content_type == 'text/plain':
                transcript_content = file_obj.read().decode('utf-8')
                transcript_content = pre_process_transcript(transcript_content)
                if not is_valid_transcript_format(transcript_content):
                    raise serializers.ValidationError(
                        "Text is not formatted correctly."
                        "Please contact developers for more information")
            # for audio files
            elif content_type in audio_content_types:
                transcript_content = get_transcription_for_audio(file_obj)
            # for other file formats
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
