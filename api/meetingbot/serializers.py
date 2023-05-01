from rest_framework import serializers
from meetingbot.models import MeetingBot

class BotStatusChangeSerializer(serializers.Serializer):
    bot_id = serializers.CharField()
    code = serializers.CharField()
    created_at = serializers.DateTimeField()
    message = serializers.CharField(allow_null=True)
    event = serializers.CharField()

    def to_representation(self, instance):
        return {
            'event': instance.event,
            'data': {
                'bot_id': instance.bot_id,
                'status': {
                    'code': instance.code,
                    'created_at': instance.created_at,
                    'message': instance.message
                    }
                }
            }


class MeetingBotSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingBot
        fields = ['id', 'status', 'transcript', 'message']
