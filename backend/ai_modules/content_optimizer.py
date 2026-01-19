from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional, Any
import logging
from datetime import datetime
from backend.models import APIResponse
from backend.utils.logging_utils import log_execution
import json
import re
from collections import Counter

logger = logging.getLogger(__name__)

router = APIRouter()

class ContentOptimizer:
    def __init__(self):
        self.optimization_config = {}
        self.optimization_rules = []
        self.performance_metrics = {}
        self.workflows = []

    async def configure_optimization(self, config: Dict[str, Any]) -> None:
        """
        Configure content optimization settings.
        
        Args:
            config (Dict[str, Any]): Optimization configuration
        """
        self.optimization_config = config
        self.optimization_rules = config.get('rules', [])
        logger.info(f"Content optimization configured: {config}")

    async def setup_optimization_workflows(self) -> None:
        """
        Set up optimization workflows for different content types.
        """
        self.workflows = [
            {
                "name": "metadata_optimization",
                "steps": [
                    "analyze_title",
                    "analyze_description",
                    "analyze_tags",
                    "analyze_thumbnail"
                ],
                "schedule": "daily"
            },
            {
                "name": "content_optimization",
                "steps": [
                    "analyze_content",
                    "analyze_engagement",
                    "analyze_audience_retention"
                ],
                "schedule": "weekly"
            },
            {
                "name": "timing_optimization",
                "steps": [
                    "analyze_posting_time",
                    "analyze_audience_activity",
                    "optimize_release_schedule"
                ],
                "schedule": "daily"
            }
        ]
        logger.info("Optimization workflows initialized")

    def analyze_title(self, title: str) -> Dict[str, Any]:
        return analyze_title(title)

    def optimize_script(self, script: str, category: str) -> Dict[str, Any]:
        return optimize_script(script, category)

    def generate_thumbnail_suggestions(self, title: str, category: str) -> List[Dict[str, Any]]:
        return generate_thumbnail_suggestions(title, category)

# Content optimization configuration
OPTIMIZATION_CONFIG = {
    "title_patterns": {
        "clickbait": [
            r"you won't believe",
            r"shocking",
            r"never seen before",
            r"mind-blowing",
            r"life-changing"
        ],
        "professional": [
            r"how to",
            r"guide to",
            r"tutorial",
            r"complete guide",
            r"step by step"
        ],
        "trending": [
            r"latest",
            r"new",
            r"2024",
            r"update",
            r"trending"
        ]
    },
    "engagement_boosters": [
        "Subscribe for more",
        "Like and share",
        "Comment below",
        "Follow for updates",
        "Join our community"
    ],
    "seo_keywords": {
        "tech": ["technology", "innovation", "digital", "software", "hardware"],
        "gaming": ["gaming", "gameplay", "stream", "esports", "gamer"],
        "education": ["learn", "education", "tutorial", "course", "study"],
        "business": ["business", "entrepreneur", "startup", "money", "success"]
    }
}

def analyze_title(title: str) -> Dict[str, Any]:
    """
    Analyze video title for optimization opportunities.
    
    Args:
        title (str): Video title
        
    Returns:
        Dict[str, Any]: Analysis results
    """
    analysis = {
        "length": len(title),
        "word_count": len(title.split()),
        "patterns": [],
        "suggestions": [],
        "score": 0
    }
    
    # Check for patterns
    for pattern_type, patterns in OPTIMIZATION_CONFIG["title_patterns"].items():
        for pattern in patterns:
            if re.search(pattern, title.lower()):
                analysis["patterns"].append({
                    "type": pattern_type,
                    "pattern": pattern
                })
    
    # Generate suggestions
    if analysis["length"] < 30:
        analysis["suggestions"].append("Title is too short. Consider adding more detail.")
    elif analysis["length"] > 100:
        analysis["suggestions"].append("Title is too long. Consider making it more concise.")
    
    if not any(pattern["type"] == "professional" for pattern in analysis["patterns"]):
        analysis["suggestions"].append("Consider adding a professional pattern for better credibility.")
    
    # Calculate score
    analysis["score"] = min(100, max(0, (
        len(analysis["patterns"]) * 20 +
        (30 <= analysis["length"] <= 100) * 30 +
        (5 <= analysis["word_count"] <= 10) * 20
    )))
    
    return analysis

def optimize_script(script: str, category: str) -> Dict[str, Any]:
    """
    Optimize video script for engagement and SEO.
    
    Args:
        script (str): Video script
        category (str): Content category
        
    Returns:
        Dict[str, Any]: Optimization results
    """
    optimization = {
        "word_count": len(script.split()),
        "paragraphs": len(script.split("\n\n")),
        "engagement_phrases": [],
        "seo_suggestions": [],
        "readability_score": 0
    }
    
    # Add engagement phrases
    for phrase in OPTIMIZATION_CONFIG["engagement_boosters"]:
        if phrase.lower() not in script.lower():
            optimization["engagement_phrases"].append(phrase)
    
    # Add SEO suggestions
    if category in OPTIMIZATION_CONFIG["seo_keywords"]:
        for keyword in OPTIMIZATION_CONFIG["seo_keywords"][category]:
            if keyword.lower() not in script.lower():
                optimization["seo_suggestions"].append(f"Consider using the keyword: {keyword}")
    
    # Calculate readability score
    words = script.split()
    avg_word_length = sum(len(word) for word in words) / len(words)
    optimization["readability_score"] = min(100, max(0, (
        100 - (avg_word_length - 4) * 10 +
        (optimization["word_count"] >= 300) * 20 +
        (optimization["paragraphs"] >= 3) * 10
    )))
    
    return optimization

def generate_thumbnail_suggestions(title: str, category: str) -> List[Dict[str, Any]]:
    """
    Generate thumbnail design suggestions.
    
    Args:
        title (str): Video title
        category (str): Content category
        
    Returns:
        List[Dict[str, Any]]: Thumbnail suggestions
    """
    suggestions = []
    
    # Extract key elements from title
    words = title.split()
    key_words = [word for word in words if len(word) > 4]
    
    # Generate color schemes based on category
    color_schemes = {
        "tech": ["#00FF00", "#000000", "#FFFFFF"],
        "gaming": ["#FF0000", "#000000", "#FFFFFF"],
        "education": ["#0000FF", "#FFFFFF", "#000000"],
        "business": ["#FFD700", "#000000", "#FFFFFF"]
    }
    
    # Create suggestions
    for i in range(3):
        suggestion = {
            "layout": f"layout_{i+1}",
            "colors": color_schemes.get(category, ["#FF0000", "#FFFFFF", "#000000"]),
            "elements": [
                {
                    "type": "text",
                    "content": " ".join(key_words[:3]),
                    "position": f"position_{i+1}"
                },
                {
                    "type": "icon",
                    "category": category,
                    "position": f"icon_position_{i+1}"
                }
            ],
            "style": f"style_{i+1}"
        }
        suggestions.append(suggestion)
    
    return suggestions

@router.post("/api/v1/optimize-title", response_model=APIResponse)
async def optimize_title_endpoint(title: str):
    """
    Analyze and optimize video title.
    
    Args:
        title (str): Video title
        
    Returns:
        APIResponse: Optimization results
    """
    try:
        analysis = analyze_title(title)
        
        log_execution(
            "title_optimization",
            "success",
            {
                "title": title,
                "score": analysis["score"]
            }
        )
        
        return APIResponse(
            status="success",
            data=analysis,
            message="Title analyzed successfully"
        )
        
    except Exception as e:
        logger.error(f"Error optimizing title: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error optimizing title: {str(e)}"
        )

@router.post("/api/v1/optimize-script", response_model=APIResponse)
async def optimize_script_endpoint(script: str, category: str):
    """
    Optimize video script.
    
    Args:
        script (str): Video script
        category (str): Content category
        
    Returns:
        APIResponse: Optimization results
    """
    try:
        optimization = optimize_script(script, category)
        
        log_execution(
            "script_optimization",
            "success",
            {
                "category": category,
                "word_count": optimization["word_count"]
            }
        )
        
        return APIResponse(
            status="success",
            data=optimization,
            message="Script optimized successfully"
        )
        
    except Exception as e:
        logger.error(f"Error optimizing script: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error optimizing script: {str(e)}"
        )

@router.post("/api/v1/suggest-thumbnail", response_model=APIResponse)
async def suggest_thumbnail_endpoint(title: str, category: str):
    """
    Generate thumbnail suggestions.
    
    Args:
        title (str): Video title
        category (str): Content category
        
    Returns:
        APIResponse: Thumbnail suggestions
    """
    try:
        suggestions = generate_thumbnail_suggestions(title, category)
        
        log_execution(
            "thumbnail_suggestions",
            "success",
            {
                "title": title,
                "category": category,
                "suggestions_count": len(suggestions)
            }
        )
        
        return APIResponse(
            status="success",
            data={"suggestions": suggestions},
            message="Thumbnail suggestions generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error generating thumbnail suggestions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating thumbnail suggestions: {str(e)}"
        ) 