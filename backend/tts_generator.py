# backend/tts_generator.py
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Dict, Optional
import logging
import os
from datetime import datetime
from backend.models import TTSRequest, APIResponse
from backend.utils.logging_utils import log_execution
import json

logger = logging.getLogger(__name__)

router = APIRouter()

# TTS Configuration
TTS_CONFIG = {
    "voices": {
        "male": {
            "en-US": ["en-US-Neural2-A", "en-US-Neural2-C", "en-US-Neural2-D"],
            "en-GB": ["en-GB-Neural2-A", "en-GB-Neural2-B", "en-GB-Neural2-C"],
            "en-AU": ["en-AU-Neural2-A", "en-AU-Neural2-B", "en-AU-Neural2-C"]
        },
        "female": {
            "en-US": ["en-US-Neural2-F", "en-US-Neural2-H", "en-US-Neural2-J"],
            "en-GB": ["en-GB-Neural2-F", "en-GB-Neural2-H", "en-GB-Neural2-J"],
            "en-AU": ["en-AU-Neural2-F", "en-AU-Neural2-H", "en-AU-Neural2-J"]
        }
    },
    "audio_formats": ["mp3", "wav", "ogg"],
    "default_format": "mp3",
    "output_dir": "audio"
}

def ensure_output_dir():
    """Ensure the output directory exists."""
    os.makedirs(TTS_CONFIG["output_dir"], exist_ok=True)

def generate_filename(voice_id: str, format: str) -> str:
    """Generate a unique filename for the audio output."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{voice_id}_{timestamp}.{format}"

def process_text(text: str, speed: float) -> str:
    """
    Process text for TTS generation.
    
    Args:
        text (str): Input text
        speed (float): Speech speed multiplier
        
    Returns:
        str: Processed text
    """
    # Add pauses for punctuation
    text = text.replace(".", ". <break time='500ms'/>")
    text = text.replace(",", ", <break time='300ms'/>")
    text = text.replace("!", "! <break time='500ms'/>")
    text = text.replace("?", "? <break time='500ms'/>")
    
    # Add speed control
    if speed != 1.0:
        text = f"<prosody rate='{speed}'>" + text + "</prosody>"
    
    return text

def _resolve_audio_encoding(texttospeech, fmt: str):
    normalized = fmt.lower().strip()
    if normalized == "mp3":
        return texttospeech.AudioEncoding.MP3
    if normalized == "wav":
        return texttospeech.AudioEncoding.LINEAR16
    if normalized == "ogg":
        return texttospeech.AudioEncoding.OGG_OPUS
    return texttospeech.AudioEncoding.MP3

async def generate_audio(
    text: str,
    voice_id: str,
    speed: float,
    format: str = TTS_CONFIG["default_format"]
) -> Dict[str, str]:
    """
    Generate audio from text using TTS service.
    
    Args:
        text (str): Text to convert to speech
        voice_id (str): Voice ID to use
        speed (float): Speech speed
        format (str): Output audio format
        
    Returns:
        Dict[str, str]: Path to generated audio file
    """
    try:
        # Ensure output directory exists
        ensure_output_dir()
        
        # Process text
        processed_text = process_text(text, speed)
        
        # Generate filename
        filename = generate_filename(voice_id, format)
        output_path = os.path.join(TTS_CONFIG["output_dir"], filename)
        
        # Implement actual TTS service integration using Google Cloud TTS
        from google.cloud import texttospeech
        from backend.config.enhanced_settings import settings
        
        # Initialize the client
        client = texttospeech.TextToSpeechClient()
        
        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(ssml=processed_text)
        
        # Build the voice request
        # Extract language code from voice_id (e.g., "en-US-Neural2-A" -> "en-US")
        language_code = "-".join(voice_id.split("-")[:2])
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_id
        )
        
        # Select the type of audio file you want returned
        audio_encoding = _resolve_audio_encoding(texttospeech, format)
        audio_config = texttospeech.AudioConfig(
            audio_encoding=audio_encoding
        )
        
        # Perform the text-to-speech request
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        # Write the response to the output file
        with open(output_path, "wb") as out:
            out.write(response.audio_content)
            logger.info(f"Successfully generated and saved audio to: {output_path}")
        
        # Log the generation
        log_execution(
            "tts_generation",
            "success",
            {
                "voice_id": voice_id,
                "speed": speed,
                "format": format,
                "output_path": output_path
            }
        )
        
        return {
            "path": output_path,
            "format": format,
            "duration": len(text.split()) / (speed * 2)  # Rough estimate
        }
        
    except Exception as e:
        logger.error(f"Error generating audio: {str(e)}")
        raise

@router.post("/api/v1/generate", response_model=APIResponse)
async def generate_tts(
    request: TTSRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate TTS audio from text.
    
    Args:
        request (TTSRequest): TTS generation parameters
        background_tasks (BackgroundTasks): FastAPI background tasks
        
    Returns:
        APIResponse: Generation status and metadata
    """
    try:
        # Validate voice ID
        valid_voices = []
        for gender in TTS_CONFIG["voices"].values():
            for voices in gender.values():
                valid_voices.extend(voices)
                
        if request.voice_id not in valid_voices:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid voice ID. Valid voices: {valid_voices}"
            )
        
        # Generate audio
        if request.format and request.format not in TTS_CONFIG["audio_formats"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid format. Valid formats: {TTS_CONFIG['audio_formats']}"
            )

        result = await generate_audio(
            request.text,
            request.voice_id,
            request.speed,
            request.format or TTS_CONFIG["default_format"]
        )
        
        return APIResponse(
            status="success",
            data=result,
            message="Audio generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error in TTS generation: {str(e)}")
        log_execution("tts_generation", "error", {"error": str(e)})
        raise HTTPException(
            status_code=500,
            detail=f"Error generating audio: {str(e)}"
        )

@router.get("/api/v1/voices", response_model=APIResponse)
async def get_voices():
    """Get available TTS voices."""
    try:
        return APIResponse(
            status="success",
            data=TTS_CONFIG["voices"],
            message="Voices retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error retrieving voices: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving voices: {str(e)}"
        )

@router.get("/api/v1/formats", response_model=APIResponse)
async def get_formats():
    """Get supported audio formats."""
    try:
        return APIResponse(
            status="success",
            data={"formats": TTS_CONFIG["audio_formats"]},
            message="Formats retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error retrieving formats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving formats: {str(e)}"
        )
