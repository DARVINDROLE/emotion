from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import uuid
import os
import time
from dotenv import load_dotenv
from services.spotify import SpotifyService
from services.googlefit import GoogleFitService
from utils.jwt import create_jwt, verify_jwt

# Load environment variables
load_dotenv()

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/authorize")
async def authorize(request: Request, platform: str = "web", provider: str = "spotify"):
    # Generate OAuth state
    state_payload = {
        "state": str(uuid.uuid4()),
        "provider": provider,
        "platform": platform,
        "exp": int(time.time()) + 300  # Expires in 5 min
    }
    state = create_jwt(state_payload)

    if provider == "spotify":
        if platform == "mobile":
            client_id = os.getenv("SPOTIFY_MOBILE_CLIENT_ID")
            client_secret = os.getenv("SPOTIFY_MOBILE_CLIENT_SECRET")
            redirect_uri = os.getenv("SPOTIFY_MOBILE_REDIRECT_URI", "myapplication://auth-success")
        else:
            client_id = os.getenv("SPOTIFY_CLIENT_ID")
            client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
            redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI", "https://emotion-k880.onrender.com/auth/callback")

        service = SpotifyService(client_id, client_secret)

    elif provider == "google":
        # Always use Web flow for Google
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "https://emotion-k880.onrender.com/auth/callback")

        service = GoogleFitService(client_id, client_secret)

    else:
        raise HTTPException(status_code=400, detail="Invalid provider")

    auth_url = service.get_authorize_url(redirect_uri, state)

    if platform == "mobile":
        return JSONResponse({"auth_url": auth_url})
    else:
        return RedirectResponse(auth_url)

@router.get("/callback")
async def callback(request: Request, code: str, state: str):
    try:
        state_data = verify_jwt(state)
        if not state_data:
            raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")

        provider = state_data.get("provider")
        platform = state_data.get("platform")

        if provider == "spotify":
            if platform == "mobile":
                client_id = os.getenv("SPOTIFY_MOBILE_CLIENT_ID")
                client_secret = os.getenv("SPOTIFY_MOBILE_CLIENT_SECRET")
                redirect_uri = os.getenv("SPOTIFY_MOBILE_REDIRECT_URI", "myapplication://auth-success")
            else:
                client_id = os.getenv("SPOTIFY_CLIENT_ID")
                client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
                redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI", "https://emotion-k880.onrender.com/auth/callback")

            service = SpotifyService(client_id, client_secret)

        elif provider == "google":
            # Use Web flow only
            client_id = os.getenv("GOOGLE_CLIENT_ID")
            client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
            redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "https://emotion-k880.onrender.com/auth/callback")

            service = GoogleFitService(client_id, client_secret)

        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        tokens = service.exchange_code_for_token(code, redirect_uri)
        user_id = str(uuid.uuid4())

        jwt_token = create_jwt({
            "user_id": user_id,
            "provider": provider,
            "access_token": tokens["access_token"],
            "refresh_token": tokens.get("refresh_token"),
            "expires_at": int(time.time()) + tokens.get("expires_in", 3600)
        })

        if platform == "mobile":
            return RedirectResponse(f"myapplication://auth-success?token={jwt_token}")
        else:
            return JSONResponse({"token": jwt_token})

    except Exception as e:
        print("❌ Callback exception:", e)
        return JSONResponse(status_code=500, content={"error": str(e)})

