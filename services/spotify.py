# services/spotify.py

import requests
import base64
import urllib.parse
import os

class SpotifyService:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = "user-read-recently-played user-top-read user-read-private"
        self.auth_url = "https://accounts.spotify.com/authorize"
        self.token_url = "https://accounts.spotify.com/api/token"
        self.api_base_url = "https://api.spotify.com/v1"

    def get_authorize_url(self, redirect_uri: str, state: str) -> str:
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": self.scope,
            "state": state,
        }
        return f"{self.auth_url}?{urllib.parse.urlencode(params)}"

    def exchange_code_for_token(self, code: str, redirect_uri: str) -> dict:
        auth_str = f"{self.client_id}:{self.client_secret}"
        b64_auth_str = base64.b64encode(auth_str.encode()).decode()

        headers = {
            "Authorization": f"Basic {b64_auth_str}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        }

        response = requests.post(self.token_url, data=data, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_user_profile(self, access_token: str) -> dict:
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = requests.get(f"{self.api_base_url}/me", headers=headers)
        response.raise_for_status()
        return response.json()

    def get_recent_tracks(self, access_token: str) -> dict:
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = requests.get(f"{self.api_base_url}/me/player/recently-played", headers=headers)
        response.raise_for_status()
        return response.json()
    
    def get_current_playing_track(self, access_token: str) -> dict:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{self.api_base_url}/me/player/currently-playing", headers=headers)
        response.raise_for_status()
        return response.json()

