# dashboard.py (now adapted for JSON response for mobile use with token refresh)

from fastapi import APIRouter, Request, HTTPException, Depends
from utils.dependencies import get_current_user
from services.googlefit import GoogleFitService
from services.spotify import SpotifyService
from database.mental_health_db import mental_health_db
import os
import time

router = APIRouter()

@router.get("/dashboard")
async def dashboard(request: Request, user=Depends(get_current_user)):
    access_token = user.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Missing access token")

    user_id = user.get("user_id")
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    google_service = GoogleFitService(client_id, client_secret)

    spotify_service = SpotifyService(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
    )

    now = int(time.time() * 1000)
    one_day_ago = now - 24 * 60 * 60 * 1000
    dataset_id = f"{one_day_ago}000000-{now}000000"

    try:
        # Google Fit data
        step_source_id = "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
        heart_source_id = "derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm"
        calories_source_id = "derived:com.google.calories.expended:com.google.android.gms:merge_calories_expended"

        steps = google_service.get_fitness_data(access_token, dataset_id, step_source_id)
        heart = google_service.get_fitness_data(access_token, dataset_id, heart_source_id)
        calories = google_service.get_fitness_data(access_token, dataset_id, calories_source_id)

        # Sleep sessions
        sessions = google_service.get_sleep_sessions(access_token, one_day_ago, now)
        sleep_summary = {
            "total_sleep_minutes": 0,
            "deep_sleep_minutes": 0,
            "light_sleep_minutes": 0
        }

        for session in sessions.get("session", []):
            if "sleep" in session.get("name", "").lower():
                start = int(session["startTimeMillis"])
                end = int(session["endTimeMillis"])
                duration_minutes = (end - start) // (1000 * 60)
                sleep_summary["total_sleep_minutes"] += duration_minutes
                sleep_summary["deep_sleep_minutes"] += int(duration_minutes * 0.25)
                sleep_summary["light_sleep_minutes"] += int(duration_minutes * 0.75)

        # Spotify data (simplified emotion tag)
        spotify_data = {
            "recent_tracks": [],
            "emotion": "calm"  # Placeholder: could be inferred from top genre or mood
        }

        # Mental health
        mental_health = mental_health_db.get_user_data(user_id) if mental_health_db else {"conditions": [], "medications": []}

        return {
            "google_fit": {
                "steps_data": steps,
                "heart_rate_data": heart,
                "calories_data": calories,
                "sleep_summary": sleep_summary,
                "sleep_sessions": sessions
            },
            "spotify": spotify_data,
            "mental_health": mental_health
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
