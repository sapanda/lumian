import requests

from app.settings import (
    ZOOM_SECRETS_BASE64,
    ZOOM_REDIRECT_URL
)

from meeting.errors import (
    ZoomException
)
import logging
logger = logging.getLogger(__name__)

AUTHORISATION_URL = 'https://zoom.us/oauth/authorize'
ACCESS_TOKEN_URL = 'https://zoom.us/oauth/token'
GET_MEETINGS_URL = 'https://api.zoom.us/v2/users/me/meetings'
GET_USER_URL = 'https://api.zoom.us/v2/users/me'


class ZoomAPI:

    def _get_response(self, url, headers, params=None):
        try:
            logger.info('Request came')
            response = requests.get(url, headers=headers, params=params)
            logger.info(response.text)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error occurred: {e}"
            status_code = e.response.status_code
            raise ZoomException(error_msg, status_code)
        except requests.exceptions.RequestException as e:
            error_msg = f"An error occurred: {e}"
            status_code = None
            raise ZoomException(error_msg, status_code)

    def _post_response(self, url, headers, data=None):
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error occurred: {e}"
            status_code = e.response.status_code
            raise ZoomException(error_msg, status_code)
        except requests.exceptions.RequestException as e:
            error_msg = f"An error occurred: {e}"
            status_code = None
            raise ZoomException(error_msg, status_code)

    def get_access_token(self, code):
        logger.debug("-- GET ACCESS TOKEN --")
        url = ACCESS_TOKEN_URL
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': ZOOM_REDIRECT_URL
        }
        headers = {
            'Authorization': f'Basic {ZOOM_SECRETS_BASE64}'
        }
        return self._post_response(url, headers, data)

    def refresh_access_token(self, refresh_token):
        logger.debug("-- REFRESH ACCESS TOKEN --")
        url = ACCESS_TOKEN_URL
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        headers = {
            'Authorization': f'Basic {ZOOM_SECRETS_BASE64}'
        }
        return self._post_response(url, headers, data)

    def is_access_token_expired(self, access_token):
        url = GET_USER_URL
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers)
        if response.status_code == 401:
            logger.debug("-- ACCESS TOKEN EXPIRED --")
            return True
        logger.debug("-- ACCESS TOKEN VALID --")
        return False

    def get_user(self, access_token):
        logger.debug("-- GET USERS --")
        url = GET_USER_URL
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        return self._get_response(url, headers)

    def get_meetings(self, access_token):
        logger.debug("-- Get MEETINGS --")
        url = f"{GET_MEETINGS_URL}?type=live"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        return self._get_response(url, headers)


zoom_api = ZoomAPI()
