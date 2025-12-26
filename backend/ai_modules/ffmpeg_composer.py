# ai_modules/ffmpeg_composer.py
import subprocess
from pathlib import Path

def compose_video(voiceover_path: str, image_path: str, music_path: str, output_path: str = "output.mp4") -> str:
    output_file = Path(output_path)

    command = [
        "ffmpeg",
        "-y",
        "-loop", "1",
        "-i", image_path,
        "-i", voiceover_path,
        "-i", music_path,
        "-filter_complex",
        "[2:a]volume=0.2[a2]; [1:a][a2]amix=inputs=2:duration=shortest",
        "-shortest",
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-pix_fmt", "yuv420p",
        str(output_file)
    ]

    subprocess.run(command, check=True)
    return str(output_file)

if __name__ == "__main__":
    composed = compose_video("audio.mp3", "thumbnail.png", "music.mp3")
    print(f"Video ready: {composed}")
