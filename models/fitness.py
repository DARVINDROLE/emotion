# fitness.py
from pydantic import BaseModel
from typing import Optional, List

class StepData(BaseModel):
    date: str
    steps: int

class HeartRateData(BaseModel):
    date: str
    min_bpm: float
    max_bpm: float
    avg_bpm: float

class SleepStagePercentage(BaseModel):
    awake: float = 0.0
    light: float = 0.0
    deep: float = 0.0
    rem: float = 0.0
    out_of_bed: float = 0.0

class SleepData(BaseModel):
    date: str
    total_minutes: float
    stages: SleepStagePercentage
    efficiency: Optional[float] = None
    bedtime: Optional[str] = None
    wakeup_time: Optional[str] = None

class CaloriesData(BaseModel):
    date: str
    calories: float

class SpotifyTrack(BaseModel):
    name: str
    artist: str
    album: Optional[str] = None
    image: Optional[str] = None
    played_at: Optional[str] = None
    valence: Optional[float] = None
    energy: Optional[float] = None
    danceability: Optional[float] = None

class DashboardData(BaseModel):
    step_data: List[StepData]
    heart_rate_data: List[HeartRateData]
    sleep_data: List[SleepData]
    calories_data: List[CaloriesData]
    current_track: Optional[SpotifyTrack]
    recent_tracks: List[SpotifyTrack]
    spotify_connected: bool