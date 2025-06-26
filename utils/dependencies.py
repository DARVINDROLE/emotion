# utils/dependencies.py (recommended new file or replace get_current_user)

from fastapi import Request, HTTPException
from utils.jwt import verify_jwt
from services.googlefit import GoogleFitService
from services.spotify import SpotifyService
import os
import time

def get_current_user(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = verify_jwt(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    access_token = payload.get("access_token")
    refresh_token = payload.get("refresh_token")
    expires_at = payload.get("expires_at", 0)
    provider = payload.get("provider")

    if time.time() > expires_at - 60 and refresh_token:
        try:
            if provider == "google":
                google_service = GoogleFitService(
                    os.getenv("GOOGLE_CLIENT_ID"),
                    os.getenv("GOOGLE_CLIENT_SECRET")
                )
                refreshed = google_service.refresh_token(refresh_token)
            elif provider == "spotify":
                spotify_service = SpotifyService(
                    os.getenv("SPOTIFY_CLIENT_ID"),
                    os.getenv("SPOTIFY_CLIENT_SECRET")
                )
                refreshed = spotify_service.refresh_token(refresh_token)
            else:
                raise HTTPException(status_code=400, detail="Unsupported provider")

            payload["access_token"] = refreshed["access_token"]
            payload["expires_at"] = int(time.time()) + refreshed.get("expires_in", 3600)

        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Token refresh failed: {str(e)}")

    return payload
