# services/spotify.py

import requests
import urllib.parse

class SpotifyService:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_url = "https://accounts.spotify.com/authorize"
        self.token_url = "https://accounts.spotify.com/api/token"
        self.api_base_url = "https://api.spotify.com/v1"

    def get_authorize_url(self, redirect_uri: str, state: str) -> str:
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": "user-read-recently-played user-read-private",
            "state": state,
            "show_dialog": "true"
        }
        return f"{self.auth_url}?{urllib.parse.urlencode(params)}"

    def exchange_code_for_token(self, code: str, redirect_uri: str) -> dict:
        print("🎧 [Spotify] Exchanging code for token...")
        print(f"   Code: {code}")
        print(f"   Redirect URI: {redirect_uri}")
        print(f"   Client ID: {self.client_id}")
        # 🔐 Avoid printing client_secret in real logs

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = requests.post(self.token_url, data=data, headers=headers)

        if not response.ok:
            print("❌ Spotify token exchange failed")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            response.raise_for_status()

        return response.json()

    def refresh_token(self, refresh_token: str) -> dict:
        print("🔁 [Spotify] Refreshing token...")
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = requests.post(self.token_url, data=data, headers=headers)

        if not response.ok:
            print("❌ Spotify token refresh failed")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            response.raise_for_status()

        return response.json()

    def get_recent_tracks(self, access_token: str, limit: int = 10) -> dict:
        print("🎵 [Spotify] Fetching recent tracks...")
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        url = f"{self.api_base_url}/me/player/recently-played"
        params = {
            "limit": limit
        }

        response = requests.get(url, headers=headers, params=params)

        if not response.ok:
            print("❌ Failed to get recent tracks")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            response.raise_for_status()

        return response.json()
