from rest_framework import serializers
from meeting.models import MeetingBot


class OAuthSerializer(serializers.Serializer):
    pass


class OauthCallbackSerializer(serializers.Serializer):
    code = serializers.CharField()


class AddBotSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    bot_name = serializers.CharField()
    meeting_url = serializers.CharField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()

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


class GetBotStatusSerializer(serializers.Serializer):
    bot_id = serializers.CharField()


class MeetingDetailsSerializer(serializers.Serializer):
    pass


class ScheduleBotSerializer(serializers.Serializer):
    calendar_email = serializers.CharField()


class CalendarStatusSerializer(serializers.Serializer):
    app = serializers.CharField()


# TODO : Cleanup Nested serialization
