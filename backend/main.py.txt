# main.py (Final version with full integration: AI logic + TTS + ROI + JWT auth + status mgmt)

from fastapi import FastAPI, Query, HTTPException, Body, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi_utils.tasks import repeat_every
from ai_modules.weekly_batch_runner import run_weekly_jobs
from pydantic import BaseModel
from ai_modules.youtube_logic import generate_ideas, channel_blueprint, simulate_roi, log_execution
from database import init_db
from typing import List, Optional
from pathlib import Path
from datetime import datetime, timedelta
import jwt
import openai

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
openai.api_key = "your-openai-api-key"

init_db()

app = FastAPI(title="YouTube Monetization MVP", version="2.0")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Auth Setup ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

fake_users_db = {
    "admin": {"username": "admin", "hashed_password": "admin", "role": "admin"},
    "editor": {"username": "editor", "hashed_password": "editor", "role": "editor"}
}

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    role: str

class VideoIdea(BaseModel):
    title: str
    category: str
    expected_views: int

class VideoIdeaDB(VideoIdea):
    id: int
    created_at: str
    status: str = "Draft"

class ROIRequest(BaseModel):
    views: int
    cpm: float = 5.0

class ROIResponse(BaseModel):
    estimated_views: int
    cpm: float
    estimated_revenue: float

class ScriptRequest(BaseModel):
    title: str
    topic: str

class ScriptResponse(BaseModel):
    title: str
    topic: str
    script: str

class TTSRequest(BaseModel):
    text: str
    voice_id: str = "default"

class TTSResponse(BaseModel):
    audio_url: str
    message: str

class StatusUpdateRequest(BaseModel):
    id: int
    status: str

# --- Auth logic ---
def verify_password(plain, hashed): return plain == hashed

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return None
    return User(username=user["username"], role=user["role"])

def create_access_token(data: dict, expires: timedelta = timedelta(minutes=30)):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + expires})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return User(username=payload.get("sub"), role=payload.get("role"))
    except:
        raise HTTPException(status_code=403, detail="Invalid token")

# --- Auth endpoints ---
@app.post("/token", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form.username, form.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me", response_model=User)
def get_me(user: User = Depends(get_current_user)): return user

# --- App endpoints ---
@app.on_event("startup")
def on_start(): init_db()

@app.get("/ideas", response_model=List[VideoIdea])
def get_ideas(topic: str = Query(...), n: int = 5):
    ideas = generate_ideas(topic, n)
    results = []
    for title in ideas:
        views = int(simulate_roi(10000))
        insert_idea(title, "AI & Monetization", views)
        results.append(VideoIdea(title=title, category="AI & Monetization", expected_views=views))
    return results

@app.get("/ideas/all", response_model=List[VideoIdeaDB])
def get_all():
    raw = fetch_all_ideas()
    return [VideoIdeaDB(id=r[0], title=r[1], category=r[2], expected_views=r[3], created_at=r[4], status=r[5] or "Draft") for r in raw]

@app.post("/ideas/status")
def set_status(req: StatusUpdateRequest, user: User = Depends(get_current_user)):
    if user.role not in ["admin", "editor"]:
        raise HTTPException(403)
    ok = update_idea_status(req.id, req.status)
    if not ok: raise HTTPException(404)
    return {"message": "Status updated"}

@app.get("/channel")
def get_channel(niche: str):
    return {"niche": niche, "blueprint": channel_blueprint(niche)}

@app.post("/roi", response_model=ROIResponse)
def calc_roi(data: ROIRequest):
    revenue = simulate_roi(data.views, data.cpm)
    return ROIResponse(estimated_views=data.views, cpm=data.cpm, estimated_revenue=revenue)

@app.post("/script", response_model=ScriptResponse)
def get_script(data: ScriptRequest):
    intro = f"Welcome! Today we explore {data.title}."
    body = f"Discover how {data.topic} shapes content creation."
    outro = "Subscribe for more!"
    return ScriptResponse(title=data.title, topic=data.topic, script="\n\n".join([intro, body, outro]))

@app.post("/tts", response_model=TTSResponse)
def tts(data: TTSRequest):
    voice_hash = str(abs(hash(data.text)))[:10]
    filename = f"{data.voice_id}-{voice_hash}.mp3"
    audio_dir = Path("static/audio")
    audio_dir.mkdir(parents=True, exist_ok=True)
    filepath = audio_dir / filename

    # Save simulated audio if doesn't exist
    if not filepath.exists():
        with open(filepath, "wb") as f:
            f.write(b"SIMULATED_MP3_AUDIO")

    audio_url = f"http://localhost:8000/static/audio/{filename}"
    return TTSResponse(audio_url=audio_url, message="Simulated TTS audio.")

@app.post("/thumbnail")
def dalle(prompt: str = Body(..., embed=True)):
    try:
        res = openai.Image.create(prompt=prompt, n=1, size="512x512")
        return {"image_url": res["data"][0]["url"]}
    except Exception as e:
        return {"error": str(e)}

@app.on_event("startup")
@repeat_every(seconds=604800)  # every 7 days
def weekly_autorun():
    print("🌀 Weekly batch auto-triggered")
    run_weekly_jobs()