# backend/script_generator.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional
import logging
from backend.models import ScriptGenerationRequest, APIResponse
from backend.utils.logging_utils import log_execution
import random

logger = logging.getLogger(__name__)

router = APIRouter()

# Script templates
SCRIPT_TEMPLATES = {
    "tutorial": {
        "intro": [
            "Hey everyone! Today we're going to learn about {topic}.",
            "Welcome to this comprehensive guide on {topic}.",
            "In this video, I'll show you everything you need to know about {topic}."
        ],
        "body": [
            "First, let's understand the basics of {topic}.",
            "Here's what you need to get started with {topic}.",
            "The key components of {topic} are:",
            "Let me walk you through the process step by step."
        ],
        "outro": [
            "That's it for today's tutorial on {topic}!",
            "I hope you found this guide helpful.",
            "Don't forget to like and subscribe for more content like this!"
        ]
    },
    "review": {
        "intro": [
            "Today we're taking a deep dive into {topic}.",
            "I've spent the last week testing {topic}, and here's what I found.",
            "Is {topic} worth your time and money? Let's find out."
        ],
        "body": [
            "Let's start with the pros of {topic}.",
            "Here are the key features that stand out:",
            "On the downside, here are some things to consider:",
            "Here's my honest opinion after testing {topic}."
        ],
        "outro": [
            "To summarize my thoughts on {topic}:",
            "Would I recommend {topic}? Here's my final verdict.",
            "Thanks for watching this review of {topic}!"
        ]
    },
    "news": {
        "intro": [
            "Breaking news in the world of {topic}!",
            "Today we're covering the latest developments in {topic}.",
            "Here's what's happening right now with {topic}."
        ],
        "body": [
            "Let's break down the key points:",
            "Here's what this means for the industry:",
            "The implications of this development are:",
            "Experts are saying:"
        ],
        "outro": [
            "That's all for this update on {topic}.",
            "Stay tuned for more news about {topic}.",
            "Don't forget to subscribe for the latest updates!"
        ]
    }
}

# Transition phrases
TRANSITIONS = [
    "Moving on to",
    "Next up",
    "Now, let's talk about",
    "Another important point is",
    "Let's not forget about",
    "Here's something interesting",
    "I want to highlight",
    "This brings us to"
]

def generate_script_sections(topic: str, style: str, duration: int) -> Dict[str, List[str]]:
    """
    Generate script sections based on style and duration.
    
    Args:
        topic (str): Main topic
        style (str): Content style (tutorial, review, news)
        duration (int): Target duration in minutes
        
    Returns:
        Dict[str, List[str]]: Generated script sections
    """
    try:
        if style not in SCRIPT_TEMPLATES:
            raise ValueError(f"Unsupported style: {style}")
            
        template = SCRIPT_TEMPLATES[style]
        sections = {
            "intro": [],
            "body": [],
            "outro": []
        }
        
        # Generate intro
        intro = random.choice(template["intro"]).format(topic=topic)
        sections["intro"].append(intro)
        
        # Generate body based on duration
        num_points = max(3, duration * 2)  # Roughly 2 points per minute
        for i in range(num_points):
            if i > 0:
                transition = random.choice(TRANSITIONS)
                sections["body"].append(f"{transition} {topic}.")
            point = random.choice(template["body"]).format(topic=topic)
            sections["body"].append(point)
            
        # Generate outro
        outro = random.choice(template["outro"]).format(topic=topic)
        sections["outro"].append(outro)
        
        return sections
        
    except Exception as e:
        logger.error(f"Error generating script sections: {str(e)}")
        raise

@router.post("/generate", response_model=APIResponse)
async def generate_script(request: ScriptGenerationRequest):
    """
    Generate a video script based on the provided parameters.
    
    Args:
        request (ScriptGenerationRequest): Script generation parameters
        
    Returns:
        APIResponse: Generated script and metadata
    """
    try:
        # Generate script sections
        sections = generate_script_sections(
            request.topic,
            request.style,
            request.duration
        )
        
        # Combine sections into full script
        script = "\n\n".join([
            "\n".join(sections["intro"]),
            "\n".join(sections["body"]),
            "\n".join(sections["outro"])
        ])
        
        # Log the execution
        log_execution(
            "script_generation",
            "success",
            {
                "topic": request.topic,
                "style": request.style,
                "duration": request.duration
            }
        )
        
        return APIResponse(
            status="success",
            data={
                "script": script,
                "sections": sections,
                "word_count": len(script.split()),
                "estimated_duration": request.duration
            },
            message="Script generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error generating script: {str(e)}")
        log_execution("script_generation", "error", {"error": str(e)})
        raise HTTPException(
            status_code=500,
            detail=f"Error generating script: {str(e)}"
        )

@router.get("/templates", response_model=APIResponse)
async def get_templates():
    """Get available script templates and styles."""
    try:
        return APIResponse(
            status="success",
            data={
                "styles": list(SCRIPT_TEMPLATES.keys()),
                "templates": SCRIPT_TEMPLATES
            },
            message="Templates retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error retrieving templates: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving templates: {str(e)}"
        )
