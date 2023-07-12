import app.settings as settings
from google_auth_oauthlib.flow import Flow
from msal import ConfidentialClientApplication
import logging
logger = logging.getLogger(__name__)

GOOGLE_SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/calendar.events.readonly',
    'https://www.googleapis.com/auth/userinfo.email'
    ]
TOKEN_URI = "https://oauth2.googleapis.com/token"
AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
REDIRECT_URI = settings.GOOGLE_REDIRECT_URL
CLIENT_ID = settings.GOOGLE_CLIENT_ID
CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET

MICROSOFT_SCOPES = [
    'https://graph.microsoft.com/User.Read',
    'https://graph.microsoft.com/Calendars.Read'
]
MICROSOFT_AUTHORITY = 'https://login.microsoftonline.com/common'
MICROSOFT_REDIRECT_URI = settings.MICROSOFT_REDIRECT_URL
MICROSOFT_CLIENT_ID = settings.MICROSOFT_CLIENT_ID
MICROSOFT_CLIENT_SECRET = settings.MICROSOFT_CLIENT_SECRET


class GoogleAPI:

    def __init__(self):
        self.flow = Flow.from_client_config(
            client_config={
                        "web": {
                            "client_id": CLIENT_ID,
                            "auth_uri": AUTH_URI,
                            "token_uri": TOKEN_URI,
                            "client_secret": CLIENT_SECRET,
                            "redirect_uris": [REDIRECT_URI]
                        }
                },
            scopes=GOOGLE_SCOPES,
            redirect_uri=REDIRECT_URI,
        )
        self.creds = None

    def get_oauth_url(self):
        logger.debug("-- Google Calendar OAuth URL --")
        auth_url, _ = self.flow.authorization_url(access_type='offline')
        return auth_url

    def get_access_token(self, code):
        logger.debug(" -- Google Calendar Access Token --")
        self.flow.fetch_token(code=code)
        creds = self.flow.credentials
        return creds.token, creds.refresh_token


class MicrosoftAPI:
    def __init__(self):
        self.app = ConfidentialClientApplication(
            MICROSOFT_CLIENT_ID,
            authority=MICROSOFT_AUTHORITY,
            client_credential=MICROSOFT_CLIENT_SECRET
        )

    def get_oauth_url(self):
        logger.debug("-- Microsoft Outlook OAuth URL --")
        auth_url = self.app.get_authorization_request_url(
            scopes=MICROSOFT_SCOPES,
            redirect_uri=MICROSOFT_REDIRECT_URI)
        return auth_url

    def get_access_token(self, code):
        logger.debug(" -- Microsoft Outlook Access Token --")
        result = self.app.acquire_token_by_authorization_code(
            code,
            scopes=MICROSOFT_SCOPES,
            redirect_uri=MICROSOFT_REDIRECT_URI)
        return result.get('access_token'), result.get('refresh_token')


class CalendarAPIFactory:
    @staticmethod
    def get_api(api_type):
        if api_type == 'google':
            return GoogleAPI()
        elif api_type == 'microsoft':
            return MicrosoftAPI()
        else:
            raise ValueError("Invalid Calendar type provided")
