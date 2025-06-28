# services/googlefit.py

import requests
import urllib.parse

class GoogleFitService:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = (
            "https://www.googleapis.com/auth/fitness.activity.read "
            "https://www.googleapis.com/auth/fitness.sleep.read"
        )
        self.auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.api_base_url = "https://www.googleapis.com/fitness/v1"

    def get_authorize_url(self, redirect_uri: str, state: str) -> str:
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": self.scope,
            "access_type": "offline",
            "include_granted_scopes": "true",
            "state": state,
            "prompt": "consent"
        }
        return f"{self.auth_url}?{urllib.parse.urlencode(params)}"

    def exchange_code_for_token(self, code: str, redirect_uri: str) -> dict:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }

        # 🔍 Debug Logging
        print("🔁 [GoogleFit] Exchanging authorization code for token...")
        print(f"   Code: {code}")
        print(f"   Redirect URI: {redirect_uri}")
        print(f"   Client ID: {self.client_id}")
        # print(f"   Client Secret: {self.client_secret}")  # Uncomment only for secure local debugging

        response = requests.post(self.token_url, data=data, headers=headers)

        if response.status_code != 200:
            print("❌ Google token exchange failed")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            response.raise_for_status()

        return response.json()

    def refresh_token(self, refresh_token: str) -> dict:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }

        response = requests.post(self.token_url, data=data, headers=headers)

        if response.status_code != 200:
            print("❌ Google token refresh failed")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            response.raise_for_status()

        return response.json()

    def get_fitness_data(self, access_token: str, dataset_id: str, data_source_id: str) -> dict:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        url = f"{self.api_base_url}/users/me/dataSources/{data_source_id}/datasets/{dataset_id}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_sleep_sessions(self, access_token: str, start_time_millis: int, end_time_millis: int) -> dict:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        url = f"{self.api_base_url}/users/me/sessions"
        params = {
            "startTimeMillis": start_time_millis,
            "endTimeMillis": end_time_millis
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
