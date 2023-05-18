from rest_framework import serializers
from meeting.models import MeetingBot


class InitiateOAuthSerializer(serializers.Serializer):
    pass


class OauthCallbackSerializer(serializers.Serializer):
    code = serializers.CharField()
    state = serializers.CharField()


class AddBotSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    bot_name = serializers.CharField()
    meeting_url = serializers.CharField()

    class Meta:
        model = MeetingBot


class BotStatusSerializer(serializers.Serializer):
    code = serializers.CharField()
    created_at = serializers.DateTimeField()
    message = serializers.CharField(allow_null=True)


class DataSerializer(serializers.Serializer):
    bot_id = serializers.CharField()
    status = BotStatusSerializer()


class BotStatusChangeSerializer(serializers.Serializer):
    data = DataSerializer()
    event = serializers.CharField()


class MeetingDetailsSerializer(serializers.Serializer):
    pass


class InitiateTranscriptionSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()


# TODO : Cleanup Nested serialization
