import requests
from rest_framework.exceptions import APIException

from app.settings import (
    ZOOM_CLIENT_ID,
    ZOOM_CLIENT_SECRET,
    ZOOM_REDIRECT_URI
)

AUTHORISATION_URL = 'https://zoom.us/oauth/authorize'
ACCESS_TOKEN_URL = 'https://zoom.us/oauth/token'
GET_MEETINGS_URL = 'https://api.zoom.us/v2/users/me/meetings'
GET_USER_URL = 'https://api.zoom.us/v2/users/me'


class ZoomOAuth:

    def get_access_token(self, code):
        url = ACCESS_TOKEN_URL
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': ZOOM_REDIRECT_URI,
            'client_id': ZOOM_CLIENT_ID,
            'client_secret': ZOOM_CLIENT_SECRET
        }
        response = requests.post(url, data=data)
        return response.json()

    def refresh_access_token(self, refresh_token):
        url = ACCESS_TOKEN_URL
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': ZOOM_CLIENT_ID,
            'client_secret': ZOOM_CLIENT_SECRET
        }
        response = requests.post(url, data=data)
        return response.json()

    def is_access_token_expired(self, access_token):
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

    def get_meetings(self):
        url = GET_MEETINGS_URL
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        response = requests.get(url, headers=headers)
        meetings = response.json().get('meetings', [])
        return meetings

zoom_oauth = ZoomOAuth()
zoom_api = ZoomAPI()