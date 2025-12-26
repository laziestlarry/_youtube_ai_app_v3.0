# main_compose_api.py (integrates ffmpeg composer)

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from ai_modules.ffmpeg_composer import compose_video
import shutil

app = FastAPI(title="Video Composer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/compose")
def compose(
    voiceover: UploadFile = File(...),
    thumbnail: UploadFile = File(...),
    music: UploadFile = File(...)
):
    tmp_dir = Path("temp")
    tmp_dir.mkdir(exist_ok=True)

    voice_path = tmp_dir / voiceover.filename
    image_path = tmp_dir / thumbnail.filename
    music_path = tmp_dir / music.filename
    out_path = tmp_dir / "rendered.mp4"

    with open(voice_path, "wb") as f:
        shutil.copyfileobj(voiceover.file, f)
    with open(image_path, "wb") as f:
        shutil.copyfileobj(thumbnail.file, f)
    with open(music_path, "wb") as f:
        shutil.copyfileobj(music.file, f)

    composed = compose_video(str(voice_path), str(image_path), str(music_path), str(out_path))
    return FileResponse(composed, media_type="video/mp4", filename="final.mp4")
