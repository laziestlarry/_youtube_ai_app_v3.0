# backend/utils.py

def generate_thumbnail(prompt: str) -> bytes:
    # This is a mock return — replace with actual image generation logic or API
    from PIL import Image
    from io import BytesIO

    img = Image.new("RGB", (512, 288), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)
    draw.text((20, 140), prompt, fill=(255, 255, 255))

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def generate_tts_audio(text: str, voice_id: str = "default") -> bytes:
    # This is a mock return — replace with real TTS logic or API
    return f"This is a TTS placeholder for: {text}".encode("utf-8")