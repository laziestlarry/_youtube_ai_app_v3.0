# backend/youtube_logic.py

import random
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging
from backend.models import VideoIdeaCreate, VideoIdeaUpdate
import json
from pathlib import Path
import re
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class VideoCategory(Enum):
    TUTORIAL = "tutorial"
    REVIEW = "review"
    NEWS = "news"
    COMPARISON = "comparison"
    VLOG = "vlog"
    REACTION = "reaction"
    INTERVIEW = "interview"
    DOCUMENTARY = "documentary"

@dataclass
class VideoMetrics:
    views: int
    likes: int
    comments: int
    shares: int
    watch_time: float
    revenue: float

# Enhanced video idea formats with categories and metadata
IDEA_FORMATS = {
    VideoCategory.TUTORIAL: [
        {
            "template": "How to {action} with {topic}",
            "description": "Step-by-step guide showing how to {action} using {topic}",
            "tags": ["how-to", "tutorial", "{topic}", "guide"]
        },
        {
            "template": "Master {topic} in {timeframe}",
            "description": "Comprehensive guide to mastering {topic} in {timeframe}",
            "tags": ["master", "learn", "{topic}", "guide"]
        }
    ],
    VideoCategory.REVIEW: [
        {
            "template": "Honest Review: {topic}",
            "description": "In-depth review of {topic} with pros, cons, and recommendations",
            "tags": ["review", "{topic}", "honest", "analysis"]
        },
        {
            "template": "{topic} Review: Pros and Cons",
            "description": "Detailed analysis of {topic} highlighting its strengths and weaknesses",
            "tags": ["review", "{topic}", "pros", "cons"]
        }
    ],
    VideoCategory.NEWS: [
        {
            "template": "Latest Updates in {topic}",
            "description": "Breaking news and latest developments in {topic}",
            "tags": ["news", "{topic}", "latest", "updates"]
        },
        {
            "template": "{topic} Trends in {year}",
            "description": "Analysis of current trends and future predictions for {topic} in {year}",
            "tags": ["trends", "{topic}", "{year}", "analysis"]
        }
    ],
    VideoCategory.COMPARISON: [
        {
            "template": "{topic} vs {alternative}: Which is Better?",
            "description": "Detailed comparison between {topic} and {alternative}",
            "tags": ["comparison", "{topic}", "{alternative}", "vs"]
        },
        {
            "template": "Comparing Top {topic} Options",
            "description": "Comprehensive comparison of the best {topic} options available",
            "tags": ["comparison", "{topic}", "best", "options"]
        }
    ]
}

# Action verbs for dynamic content
ACTIONS = [
    "master", "learn", "implement", "optimize", "scale",
    "automate", "monetize", "grow", "build", "create",
    "develop", "design", "launch", "manage", "improve"
]

# Timeframes for tutorials
TIMEFRAMES = [
    "30 Days", "1 Week", "24 Hours", "5 Minutes",
    "10 Steps", "3 Easy Steps", "2 Hours", "1 Month"
]

# Topic modifiers for variety
TOPIC_MODIFIERS = [
    "Complete", "Ultimate", "Advanced", "Beginner's",
    "Professional", "Expert", "Essential", "Comprehensive"
]

def clean_topic(topic: str) -> str:
    """
    Clean and format a topic string.
    
    Args:
        topic (str): Raw topic string
        
    Returns:
        str: Cleaned topic string
    """
    # Remove special characters and extra spaces
    cleaned = re.sub(r'[^\w\s-]', '', topic)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip().capitalize()

def generate_ideas(
    topic: str,
    n: int = 5,
    category: Optional[VideoCategory] = None,
    min_views: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Generate YouTube video title ideas with enhanced variety and relevance.

    Args:
        topic (str): Input topic or keyword
        n (int): Number of ideas to return
        category (Optional[VideoCategory]): Specific category to generate ideas for
        min_views (Optional[int]): Minimum expected views threshold

    Returns:
        List[Dict[str, Any]]: Generated video ideas with metadata
    """
    try:
        topic_clean = clean_topic(topic)
        ideas = []
        
        # Select categories to use
        categories = [category] if category else list(VideoCategory)
        
        attempts = 0
        max_attempts = n * 3  # Allow some extra attempts to meet minimum views
        
        while len(ideas) < n and attempts < max_attempts:
            attempts += 1
            
            # Select random category and format
            selected_category = random.choice(categories)
            format_data = random.choice(IDEA_FORMATS[selected_category])
            format_template = format_data["template"]
            
            # Generate dynamic content
            if "{action}" in format_template:
                format_template = format_template.format(
                    action=random.choice(ACTIONS),
                    topic=topic_clean
                )
            elif "{timeframe}" in format_template:
                format_template = format_template.format(
                    topic=topic_clean,
                    timeframe=random.choice(TIMEFRAMES)
                )
            elif "{year}" in format_template:
                format_template = format_template.format(
                    topic=topic_clean,
                    year=datetime.now().year + 1
                )
            elif "{alternative}" in format_template:
                # Generate a related alternative topic
                alternative = f"Alternative {topic_clean}"
                format_template = format_template.format(
                    topic=topic_clean,
                    alternative=alternative
                )
            else:
                format_template = format_template.format(topic=topic_clean)
            
            # Add random modifier for variety
            if random.random() < 0.3:  # 30% chance to add a modifier
                modifier = random.choice(TOPIC_MODIFIERS)
                format_template = f"{modifier} {format_template}"
            
            # Calculate expected views
            expected_views = calculate_expected_views(selected_category, topic_clean)
            
            # Skip if below minimum views threshold
            if min_views and expected_views < min_views:
                continue
            
            # Generate description and tags
            description = format_data["description"].format(
                topic=topic_clean,
                action=random.choice(ACTIONS) if "{action}" in format_data["description"] else "",
                timeframe=random.choice(TIMEFRAMES) if "{timeframe}" in format_data["description"] else "",
                year=datetime.now().year + 1 if "{year}" in format_data["description"] else ""
            )
            
            tags = [tag.format(
                topic=topic_clean.lower(),
                year=str(datetime.now().year + 1) if "{year}" in tag else ""
            ) for tag in format_data["tags"]]
            
            ideas.append({
                "title": format_template,
                "description": description,
                "category": selected_category.value,
                "expected_views": expected_views,
                "tags": tags,
                "created_at": datetime.utcnow().isoformat(),
                "metadata": {
                    "difficulty": random.choice(["Beginner", "Intermediate", "Advanced"]),
                    "estimated_duration": f"{random.randint(5, 30)} minutes",
                    "target_audience": random.choice([
                        "General Audience",
                        "Professionals",
                        "Students",
                        "Enthusiasts"
                    ])
                }
            })
        
        logger.info(f"Generated {len(ideas)} ideas for topic: {topic}")
        return ideas
    
    except Exception as e:
        logger.error(f"Error generating ideas: {str(e)}")
        raise

def calculate_expected_views(category: VideoCategory, topic: str) -> int:
    """
    Calculate expected views based on category and topic relevance.
    
    Args:
        category (VideoCategory): Video category
        topic (str): Video topic
        
    Returns:
        int: Estimated view count
    """
    # Base view counts by category
    base_views = {
        VideoCategory.TUTORIAL: 5000,
        VideoCategory.REVIEW: 8000,
        VideoCategory.NEWS: 3000,
        VideoCategory.COMPARISON: 6000,
        VideoCategory.VLOG: 4000,
        VideoCategory.REACTION: 7000,
        VideoCategory.INTERVIEW: 4500,
        VideoCategory.DOCUMENTARY: 5500
    }
    
    # Get base views for category
    views = base_views.get(category, 4000)
    
    # Add random variation
    variation = random.uniform(0.5, 1.5)
    
    # Topic length factor (longer topics tend to get more views)
    topic_length_factor = 1 + (len(topic.split()) * 0.1)
    
    # Seasonal factor (videos published in Q4 tend to get more views)
    current_month = datetime.now().month
    seasonal_factor = 1.2 if current_month in [10, 11, 12] else 1.0
    
    return int(views * variation * topic_length_factor * seasonal_factor)

def channel_blueprint(niche: str) -> Dict[str, Any]:
    """
    Generate a comprehensive channel blueprint from a niche.

    Args:
        niche (str): The niche to build a YouTube channel around.

    Returns:
        Dict[str, Any]: Detailed blueprint including content and monetization strategy.
    """
    try:
        niche_clean = clean_topic(niche)
        
        # Generate content schedule
        content_schedule = {
            "weekly": [
                {
                    "day": "Monday",
                    "type": "Main Video",
                    "format": "Tutorial/How-to"
                },
                {
                    "day": "Wednesday",
                    "type": "Short",
                    "format": "Quick Tips"
                },
                {
                    "day": "Friday",
                    "type": "Main Video",
                    "format": "Review/Comparison"
                },
                {
                    "day": "Saturday",
                    "type": "Live Stream",
                    "format": "Q&A/Community"
                }
            ],
            "monthly": [
                {
                    "type": "Special Series",
                    "format": "Deep Dive",
                    "frequency": "First week of month"
                },
                {
                    "type": "Collaboration",
                    "format": "Guest Interview",
                    "frequency": "Third week of month"
                }
            ]
        }
        
        # Generate monetization strategy
        monetization = {
            "primary": [
                {
                    "method": "YouTube Ad Revenue",
                    "description": "Optimize for mid-roll ads and high CPM content",
                    "estimated_revenue": "40% of total income"
                },
                {
                    "method": "Sponsorships",
                    "description": "Brand deals and product placements",
                    "estimated_revenue": "30% of total income"
                }
            ],
            "secondary": [
                {
                    "method": "Affiliate Marketing",
                    "description": "Product recommendations with affiliate links",
                    "estimated_revenue": "15% of total income"
                },
                {
                    "method": "Digital Products",
                    "description": "Courses, ebooks, and templates",
                    "estimated_revenue": "10% of total income"
                },
                {
                    "method": "Membership Program",
                    "description": "Exclusive content and community access",
                    "estimated_revenue": "5% of total income"
                }
            ]
        }
        
        # Generate growth strategy
        growth_strategy = {
            "content_optimization": [
                "SEO-optimized titles and descriptions",
                "Engaging thumbnails and hooks",
                "Consistent branding and style",
                "Strategic use of cards and end screens"
            ],
            "audience_engagement": [
                "Regular community posts",
                "Comment response strategy",
                "Live stream Q&A sessions",
                "Community polls and feedback"
            ],
            "cross_promotion": [
                "Social media presence",
                "Email newsletter",
                "Collaboration with other creators",
                "Guest appearances on podcasts"
            ],
            "analytics_tracking": [
                "View duration optimization",
                "Audience retention analysis",
                "Traffic source monitoring",
                "Demographic targeting"
            ]
        }
        
        return {
            "channel_name": f"{niche_clean} Central",
            "content_schedule": content_schedule,
            "monetization": monetization,
            "growth_strategy": growth_strategy,
            "target_metrics": {
                "first_month": {
                    "subscribers": 1000,
                    "views": 5000,
                    "engagement_rate": 0.05
                },
                "six_months": {
                    "subscribers": 10000,
                    "views": 50000,
                    "engagement_rate": 0.07
                },
                "one_year": {
                    "subscribers": 50000,
                    "views": 250000,
                    "engagement_rate": 0.08
                }
            }
        }
    except Exception as e:
        logger.error(f"Error generating channel blueprint: {str(e)}")
        raise

def simulate_roi(
    views: int,
    cpm: float = 5.0,
    engagement_rate: float = 0.05,
    subscriber_rate: float = 0.02
) -> Dict[str, Any]:
    """
    Simulate potential revenue and engagement metrics.

    Args:
        views (int): Estimated number of views
        cpm (float): Cost per 1000 impressions
        engagement_rate (float): Expected engagement rate
        subscriber_rate (float): Expected subscriber conversion rate

    Returns:
        Dict[str, Any]: Revenue and engagement metrics
    """
    try:
        # Calculate revenue
        ad_revenue = round((views / 1000) * cpm, 2)
        
        # Calculate engagement metrics
        likes = int(views * engagement_rate)
        comments = int(likes * 0.1)  # 10% of likes
        shares = int(views * engagement_rate * 0.05)  # 5% of engaged viewers
        
        # Calculate subscriber gain
        new_subscribers = int(views * subscriber_rate)
        
        # Calculate watch time (assuming 50% of video length watched)
        avg_video_length = 10  # minutes
        watch_time = round(views * (avg_video_length * 0.5), 2)
        
        # Calculate additional revenue streams
        sponsorship_revenue = round(ad_revenue * 0.5, 2)  # 50% of ad revenue
        affiliate_revenue = round(ad_revenue * 0.3, 2)  # 30% of ad revenue
        
        total_revenue = round(ad_revenue + sponsorship_revenue + affiliate_revenue, 2)
        
        return {
            "revenue": {
                "ad_revenue": ad_revenue,
                "sponsorship_revenue": sponsorship_revenue,
                "affiliate_revenue": affiliate_revenue,
                "total_revenue": total_revenue
            },
            "engagement": {
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "watch_time_minutes": watch_time
            },
            "growth": {
                "new_subscribers": new_subscribers,
                "subscriber_growth_rate": f"{subscriber_rate * 100}%"
            },
            "metrics": {
                "engagement_rate": f"{engagement_rate * 100}%",
                "cpm": f"${cpm}",
                "average_watch_time": f"{avg_video_length * 0.5} minutes"
            }
        }
    except Exception as e:
        logger.error(f"Error simulating ROI: {str(e)}")
        raise

def log_execution(
    action: str,
    status: str = "success",
    details: Optional[Dict] = None,
    error: Optional[str] = None
) -> Dict[str, Any]:
    """
    Log an execution event with enhanced error handling and metadata.

    Args:
        action (str): Action performed
        status (str): Status of the action
        details (Optional[Dict]): Additional details
        error (Optional[str]): Error message if any

    Returns:
        Dict[str, Any]: Log entry with metadata
    """
    try:
        log_entry = {
            "action": action,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {},
            "error": error,
            "metadata": {
                "environment": "production",
                "version": "1.0.0"
            }
        }
        
        # Log to file
        log_file = Path("logs/execution.log")
        log_file.parent.mkdir(exist_ok=True)
        
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        
        return log_entry
    except Exception as e:
        logger.error(f"Error logging execution: {str(e)}")
        raise
