import app.settings as settings
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

import logging
logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
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

    def _build_creds(self, access_token, refresh_token):
        self.creds = Credentials.from_authorized_user_info(
                    info={
                            "token": access_token,
                            "refresh_token": refresh_token,
                            "token_uri": TOKEN_URI,
                            "client_id": CLIENT_ID,
                            "client_secret": CLIENT_SECRET
                        },
                    scopes=SCOPES
                )

    def get_oauth_url(self):
        logger.debug("-- Calendar OAuth URL --")
        auth_url, _ = self.flow.authorization_url(access_type='offline')
        return auth_url

    def get_access_token(self, code):
        logger.debug(" -- Calendar Access Token --")
        self.flow.fetch_token(code=code)
        return self.flow.credentials

    def is_access_token_expired(self, access_token, refresh_token):
        self._build_creds(access_token, refresh_token)
        if self.creds.expired and self.creds.refresh_token:
            logger.debug("-- Calendar Token Expired --")
            self.creds.refresh(Request())
            return True, self.creds
        return False

    def _fetch_meeting_urls(self, events):

        meeting_urls = []
        for event in events:
            if 'location' in event:
                meeting_url = event['location']
                meeting_urls.append(meeting_url)

        return meeting_urls
        # Add more conditions for other conference providers here

    def get_meeting_urls(self):
        logger.debug("-- Calendar Get Meetings --")
        service = build('calendar', 'v3', credentials=self.creds)
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=10,  # Maximum number of events to fetch
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        return self._fetch_meeting_urls(events)


google_api = GoogleAPI()
