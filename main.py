# main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from routes import auth, fitness 
from routes import spotify
import os

app = FastAPI()

# Allow mobile apps and web apps to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend domain(s) in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session middleware for OAuth state tracking
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("FLASK_SECRET_KEY", "super-secret-key-123")
)

# Templates directory (for index.html)
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(auth.router, prefix="/auth")
app.include_router(fitness.router)
app.include_router(spotify.router)
                   
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)
