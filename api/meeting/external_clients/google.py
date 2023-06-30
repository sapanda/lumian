import app.settings as settings
from google_auth_oauthlib.flow import Flow
import logging
logger = logging.getLogger(__name__)

SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/calendar.events.readonly',
    'https://www.googleapis.com/auth/userinfo.email'
    ]
TOKEN_URI = "https://oauth2.googleapis.com/token"
AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
REDIRECT_URI = settings.GOOGLE_REDIRECT_URL
CLIENT_ID = settings.GOOGLE_CLIENT_ID
CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET


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
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI,
        )
        self.creds = None

    def get_oauth_url(self):
        logger.debug("-- Calendar OAuth URL --")
        auth_url, _ = self.flow.authorization_url(access_type='offline')
        return auth_url

    def get_access_token(self, code):
        logger.debug(" -- Calendar Access Token --")
        self.flow.fetch_token(code=code)
        creds = self.flow.credentials
        return creds.token, creds.refresh_token


google_api = GoogleAPI()
