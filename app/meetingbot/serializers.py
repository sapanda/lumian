from rest_framework import serializers

class CreateBotAPISerializer(serializers.Serializer):

   bot_name = serializers.CharField()
   meeting_url = serializers.CharField()