from rest_framework.exceptions import APIException
from rest_framework import status

class MeetingBotException(APIException):

    default_code = "Meeting Bot Exception"

    def __init__(self, message, status_code):
        self.status_code = status_code
        self.detail = message
        super().__init__(detail=message, code=self.default_code)
    
class RecallAITimeoutException(MeetingBotException):
    pass

