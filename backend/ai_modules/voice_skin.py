# ai_modules/voice_skin.py

VOICE_SKINS = {
    "elevenlabs-premium": {
        "emotion": "warm",
        "pitch_shift": 0,
        "speed": 1.0,
        "style": "storytelling"
    },
    "coqui-actor": {
        "emotion": "dramatic",
        "pitch_shift": -2,
        "speed": 0.9,
        "style": "cinematic"
    },
    "google-neural": {
        "emotion": "neutral",
        "pitch_shift": 1,
        "speed": 1.05,
        "style": "explainer"
    }
}

def get_voice_skin(name: str) -> dict:
    return VOICE_SKINS.get(name, VOICE_SKINS["google-neural"])

if __name__ == "__main__":
    for name in VOICE_SKINS:
        print(f"Skin '{name}':", get_voice_skin(name))
