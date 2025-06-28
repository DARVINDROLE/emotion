from fastapi import APIRouter, Depends, HTTPException
from utils.dependencies import get_current_user
from services.spotify import SpotifyService
import os

router = APIRouter(prefix="/api/spotify", tags=["Spotify"])

# Load credentials
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
spotify_service = SpotifyService(client_id, client_secret)

@router.get("/recent")
async def get_recent_tracks(user=Depends(get_current_user)):
    access_token = user.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Missing Spotify access token")

    try:
        recent_tracks = spotify_service.get_recent_tracks(access_token)
        return {
            "tracks": recent_tracks,
            "emotion": "calm"  # Replace this with genre-to-emotion logic if needed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
