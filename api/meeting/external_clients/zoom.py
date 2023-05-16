import requests

from app.settings import (
    ZOOM_CLIENT_ID,
    ZOOM_CLIENT_SECRET,
    ZOOM_REDIRECT_URL
)

from meeting.errors import (
    ZoomOauthException,
    ZoomAPIException
)
import logging
logger = logging.getLogger(__name__)

AUTHORISATION_URL = 'https://zoom.us/oauth/authorize'
ACCESS_TOKEN_URL = 'https://zoom.us/oauth/token'
GET_MEETINGS_URL = 'https://api.zoom.us/v2/users/me/meetings'
GET_USER_URL = 'https://api.zoom.us/v2/users/me'


class ZoomOAuth:

    def _get_response(self, url, data):
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error occurred: {e}"
            status_code = e.response.status_code
            raise ZoomOauthException(error_msg, status_code)
        except requests.exceptions.RequestException as e:
            error_msg = f"An error occurred: {e}"
            status_code = None
            raise ZoomOauthException(error_msg, status_code)

    def get_access_token(self, code):
        logger.debug("-- GET ACCESS TOKEN --")
        url = ACCESS_TOKEN_URL
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': ZOOM_REDIRECT_URL,
            'client_id': ZOOM_CLIENT_ID,
            'client_secret': ZOOM_CLIENT_SECRET
        }
        return self._get_response(url, data)

    def refresh_access_token(self, refresh_token):
        logger.debug("-- REFRESH ACCESS TOKEN --")
        url = ACCESS_TOKEN_URL
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': ZOOM_CLIENT_ID,
            'client_secret': ZOOM_CLIENT_SECRET
        }

        return self._get_response(url, data)

    def is_access_token_expired(self, access_token):
        logger.debug("-- ACCESS TOKEN EXPIRED --")
        url = GET_USER_URL
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 401:
            return True
        return False


class ZoomAPI:

    def __init__(self, access_token):
        self.access_token = access_token

    def _get_response(self, url, headers):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error occurred: {e}"
            status_code = e.response.status_code
            raise ZoomAPIException(error_msg, status_code)
        except requests.exceptions.RequestException as e:
            error_msg = f"An error occurred: {e}"
            status_code = None
            raise ZoomAPIException(error_msg, status_code)

    def get_user(self):
        logger.debug("-- GET USERS --")
        url = GET_USER_URL
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        return self._get_response(url, headers)

    def get_meetings(self):
        logger.debug("-- Get MEETINGS --")
        url = f"{GET_MEETINGS_URL}?type=live"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        return self._get_response(url, headers)
