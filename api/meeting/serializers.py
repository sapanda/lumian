from rest_framework import serializers
from meeting.models import MeetingBot


class InitiateTranscriptionSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    

class AddBotSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    bot_name = serializers.CharField()
    meeting_url = serializers.CharField()

    class Meta:
        model = MeetingBot


class MeetingDetailsSerializer(serializers.Serializer):

    def validate(self, attrs):
        """
        Verify that the incoming request belongs to the current user.
        """
        request = self.context.get('request')
        if request.user != attrs.get('user'):
            raise serializers.ValidationError("Invalid user.")
        return attrs


class OauthCallbackSerializer(serializers.Serializer):
    code = serializers.CharField()
    state = serializers.CharField()


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


class MeetingBotSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingBot
        fields = ['id', 'status', 'transcript', 'message']


# TODO : Cleanup Nested serialization
