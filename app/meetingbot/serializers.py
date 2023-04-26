from rest_framework import serializers
from meetingbot.models import MeetingBot

class CreateBotAPISerializer(serializers.Serializer):

   bot_name = serializers.CharField()
   meeting_url = serializers.CharField()


class BotStatusSerializer(serializers.Serializer):

    code = serializers.CharField()
    created_at = serializers.DateTimeField()
    message = serializers.CharField(allow_null=True)

class DataSerializer(serializers.Serializer):
    bot_id = serializers.CharField()
    status = BotStatusSerializer()


class BotStatusChangeSerializer(serializers.Serializer):
    data = DataSerializer()
    even = serializers.CharField()


    
