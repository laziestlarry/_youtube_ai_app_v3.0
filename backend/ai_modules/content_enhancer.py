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

class ContentEnhancer:
    def __init__(self):
        self.templates = {
            "intro": [
                "Hey everyone! Today we're going to talk about {topic}.",
                "Welcome to this video about {topic}!",
                "In this video, I'll show you everything about {topic}."
            ],
            "outro": [
                "Thanks for watching! Don't forget to like and subscribe for more content like this.",
                "That's it for today! Let me know in the comments what you thought.",
                "Hope you enjoyed this video! See you in the next one."
            ],
            "transitions": [
                "Now, let's move on to...",
                "Next up, we have...",
                "Moving forward, we'll look at..."
            ]
        }
        
        self.engagement_phrases = [
            "What do you think about this?",
            "Let me know in the comments below!",
            "Share your thoughts with us!",
            "Would you like to see more content like this?"
        ]
        
        self.enhancement_config = {}
        self.enhancement_rules = []
        self.quality_metrics = {}
        self.workflows = []
    
    async def configure_enhancement(self, config: Dict[str, Any]) -> None:
        """
        Configure content enhancement settings.
        
        Args:
            config (Dict[str, Any]): Enhancement configuration
        """
        self.enhancement_config = config
        self.enhancement_rules = config.get('rules', [])
        logger.info(f"Content enhancement configured: {config}")
    
    async def setup_enhancement_workflows(self) -> None:
        """
        Set up enhancement workflows for different content types.
        """
        self.workflows = [
            {
                "name": "script_enhancement",
                "steps": [
                    "enhance_script",
                    "optimize_structure",
                    "add_hooks"
                ],
                "schedule": "on_demand"
            },
            {
                "name": "visual_enhancement",
                "steps": [
                    "enhance_thumbnail",
                    "optimize_visuals",
                    "add_overlays"
                ],
                "schedule": "on_demand"
            },
            {
                "name": "engagement_enhancement",
                "steps": [
                    "add_call_to_action",
                    "optimize_interaction",
                    "enhance_community"
                ],
                "schedule": "on_demand"
            }
        ]
        logger.info("Enhancement workflows initialized")
    
    def enhance_script(self, script: str, category: str) -> Dict[str, any]:
        """
        Enhance video script with AI-powered improvements.
        
        Args:
            script (str): Original script
            category (str): Content category
            
        Returns:
            Dict[str, any]: Enhanced script and suggestions
        """
        enhanced = {
            "original": script,
            "enhanced": self._apply_enhancements(script, category),
            "suggestions": self._generate_suggestions(script, category),
            "engagement_opportunities": self._identify_engagement_opportunities(script)
        }
        
        return enhanced
    
    def generate_hooks(self, topic: str, category: str) -> List[str]:
        """
        Generate attention-grabbing hooks for videos.
        
        Args:
            topic (str): Video topic
            category (str): Content category
            
        Returns:
            List[str]: Generated hooks
        """
        hooks = []
        
        # Question hooks
        hooks.append(f"Did you know that {topic} can change your life?")
        hooks.append(f"Want to learn everything about {topic}?")
        hooks.append(f"The truth about {topic} that nobody tells you...")
        
        # Story hooks
        hooks.append(f"I discovered something amazing about {topic}...")
        hooks.append(f"This is how I mastered {topic} in just one week...")
        
        # Value hooks
        hooks.append(f"Learn how to {topic} like a pro!")
        hooks.append(f"The ultimate guide to {topic} that you need to see...")
        
        return hooks
    
    def optimize_script_structure(self, script: str) -> Dict[str, any]:
        """
        Optimize script structure for better engagement.
        
        Args:
            script (str): Original script
            
        Returns:
            Dict[str, any]: Structure optimization results
        """
        paragraphs = script.split("\n\n")
        
        analysis = {
            "paragraph_count": len(paragraphs),
            "avg_paragraph_length": sum(len(p.split()) for p in paragraphs) / len(paragraphs),
            "suggestions": [],
            "restructured_script": self._restructure_script(paragraphs)
        }
        
        # Generate suggestions
        if analysis["paragraph_count"] < 3:
            analysis["suggestions"].append("Consider breaking down the content into more paragraphs for better readability")
        
        if analysis["avg_paragraph_length"] > 100:
            analysis["suggestions"].append("Some paragraphs are too long. Consider splitting them for better engagement")
        
        return analysis
    
    def _apply_enhancements(self, script: str, category: str) -> str:
        """Apply various enhancements to the script."""
        enhanced = script
        
        # Add transitions
        paragraphs = enhanced.split("\n\n")
        for i in range(1, len(paragraphs)):
            if not any(transition in paragraphs[i] for transition in self.templates["transitions"]):
                paragraphs[i] = f"{self.templates['transitions'][i % len(self.templates['transitions'])]} {paragraphs[i]}"
        
        enhanced = "\n\n".join(paragraphs)
        
        # Add engagement phrases
        if len(paragraphs) > 2:
            mid_point = len(paragraphs) // 2
            paragraphs.insert(mid_point, self.engagement_phrases[0])
            enhanced = "\n\n".join(paragraphs)
        
        return enhanced
    
    def _generate_suggestions(self, script: str, category: str) -> List[str]:
        """Generate content improvement suggestions."""
        suggestions = []
        
        # Length suggestions
        word_count = len(script.split())
        if word_count < 300:
            suggestions.append("Consider expanding the content for better value delivery")
        elif word_count > 2000:
            suggestions.append("Consider breaking down the content into multiple videos")
        
        # Structure suggestions
        paragraphs = script.split("\n\n")
        if len(paragraphs) < 3:
            suggestions.append("Add more structure to the content with clear sections")
        
        # Engagement suggestions
        if not any(phrase in script.lower() for phrase in self.engagement_phrases):
            suggestions.append("Add more engagement prompts throughout the content")
        
        return suggestions
    
    def _identify_engagement_opportunities(self, script: str) -> List[Dict[str, any]]:
        """Identify opportunities for audience engagement."""
        opportunities = []
        
        # Find key points for questions
        sentences = script.split(". ")
        for i, sentence in enumerate(sentences):
            if len(sentence.split()) > 10 and i % 3 == 0:
                opportunities.append({
                    "type": "question",
                    "position": i,
                    "suggestion": f"Ask viewers about their experience with: {sentence[:50]}..."
                })
        
        # Find opportunities for calls to action
        for i, paragraph in enumerate(script.split("\n\n")):
            if len(paragraph.split()) > 50 and i % 2 == 0:
                opportunities.append({
                    "type": "call_to_action",
                    "position": i,
                    "suggestion": "Add a call to action here to encourage engagement"
                })
        
        return opportunities
    
    def _restructure_script(self, paragraphs: List[str]) -> str:
        """Restructure script for better flow and engagement."""
        restructured = []
        
        # Add intro
        restructured.append(self.templates["intro"][0])
        
        # Add main content with transitions
        for i, paragraph in enumerate(paragraphs):
            if i > 0:
                restructured.append(self.templates["transitions"][i % len(self.templates["transitions"])])
            restructured.append(paragraph)
        
        # Add outro
        restructured.append(self.templates["outro"][0])
        
        return "\n\n".join(restructured)

# Initialize content enhancer
content_enhancer = ContentEnhancer()

@router.post("/enhance-script", response_model=APIResponse)
async def enhance_script_endpoint(script: str, category: str):
    """
    Enhance video script with AI-powered improvements.
    
    Args:
        script (str): Original script
        category (str): Content category
        
    Returns:
        APIResponse: Enhanced script and suggestions
    """
    try:
        enhanced = content_enhancer.enhance_script(script, category)
        
        log_execution(
            "script_enhancement",
            "success",
            {
                "category": category,
                "original_length": len(script),
                "enhanced_length": len(enhanced["enhanced"])
            }
        )
        
        return APIResponse(
            status="success",
            data=enhanced,
            message="Script enhanced successfully"
        )
        
    except Exception as e:
        logger.error(f"Error enhancing script: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error enhancing script: {str(e)}"
        )

@router.post("/generate-hooks", response_model=APIResponse)
async def generate_hooks_endpoint(topic: str, category: str):
    """
    Generate attention-grabbing hooks for videos.
    
    Args:
        topic (str): Video topic
        category (str): Content category
        
    Returns:
        APIResponse: Generated hooks
    """
    try:
        hooks = content_enhancer.generate_hooks(topic, category)
        
        log_execution(
            "hook_generation",
            "success",
            {
                "topic": topic,
                "category": category,
                "hooks_generated": len(hooks)
            }
        )
        
        return APIResponse(
            status="success",
            data={"hooks": hooks},
            message="Hooks generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error generating hooks: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating hooks: {str(e)}"
        )

@router.post("/optimize-structure", response_model=APIResponse)
async def optimize_structure_endpoint(script: str):
    """
    Optimize script structure for better engagement.
    
    Args:
        script (str): Original script
        
    Returns:
        APIResponse: Structure optimization results
    """
    try:
        optimization = content_enhancer.optimize_script_structure(script)
        
        log_execution(
            "structure_optimization",
            "success",
            {
                "original_length": len(script),
                "optimized_length": len(optimization["restructured_script"])
            }
        )
        
        return APIResponse(
            status="success",
            data=optimization,
            message="Script structure optimized successfully"
        )
        
    except Exception as e:
        logger.error(f"Error optimizing structure: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error optimizing structure: {str(e)}"
        ) 