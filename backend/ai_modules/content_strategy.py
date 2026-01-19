from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional, Any
import logging
from datetime import datetime, timedelta
from backend.models import APIResponse
from backend.utils.logging_utils import log_execution
import json
import requests
from decimal import Decimal

logger = logging.getLogger(__name__)
router = APIRouter()

class ContentStrategyOptimizer:
    def __init__(self):
        self.content_parameters = {
            "video_length": {
                "optimal": 10,  # minutes
                "weight": 0.2
            },
            "engagement_metrics": {
                "likes_to_views": 0.05,
                "comments_to_views": 0.01,
                "shares_to_views": 0.02,
                "weight": 0.3
            },
            "monetization": {
                "cpm_rate": 2.00,
                "sponsorship_rate": 0.05,
                "affiliate_rate": 0.10,
                "weight": 0.3
            },
            "growth_metrics": {
                "subscriber_conversion": 0.02,
                "retention_rate": 0.6,
                "weight": 0.2
            }
        }
        
        self.trending_topics = []
        self.competitor_analysis = {}
        self.audience_insights = {}
        self.strategy_config = {}
        self.content_calendar = []
    
    async def configure_strategy(self, config: Dict[str, Any]) -> None:
        """
        Configure content strategy settings.
        
        Args:
            config (Dict[str, Any]): Strategy configuration
        """
        self.strategy_config = config
        logger.info(f"Content strategy configured: {config}")
    
    async def setup_content_calendar(self) -> None:
        """
        Set up content calendar with optimal posting schedule.
        """
        self.content_calendar = [
            {
                "day": "Monday",
                "time": "12:00",
                "type": "tutorial",
                "topic": "Getting Started"
            },
            {
                "day": "Wednesday",
                "time": "15:00",
                "type": "entertainment",
                "topic": "Highlights"
            },
            {
                "day": "Friday",
                "time": "18:00",
                "type": "educational",
                "topic": "Deep Dive"
            }
        ]
        logger.info("Content calendar initialized")
    
    def analyze_content_performance(self, video_data: Dict) -> Dict:
        """
        Analyze video performance and provide optimization recommendations.
        
        Args:
            video_data (Dict): Video performance data
            
        Returns:
            Dict: Analysis results and recommendations
        """
        try:
            # Calculate performance score
            performance_score = self._calculate_performance_score(video_data)
            
            # Generate optimization recommendations
            recommendations = self._generate_recommendations(video_data, performance_score)
            
            # Predict potential growth
            growth_prediction = self._predict_growth(video_data, recommendations)
            
            return {
                "performance_score": performance_score,
                "recommendations": recommendations,
                "growth_prediction": growth_prediction
            }
            
        except Exception as e:
            logger.error(f"Error analyzing content performance: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error analyzing content: {str(e)}"
            )
    
    def _calculate_performance_score(self, video_data: Dict) -> float:
        """Calculate overall performance score."""
        try:
            scores = []
            
            # Video length score
            length_score = 1 - abs(video_data.get("duration", 0) - self.content_parameters["video_length"]["optimal"]) / self.content_parameters["video_length"]["optimal"]
            scores.append(length_score * self.content_parameters["video_length"]["weight"])
            
            # Engagement score
            engagement_score = (
                video_data.get("likes", 0) / max(video_data.get("views", 1), 1) * self.content_parameters["engagement_metrics"]["likes_to_views"] +
                video_data.get("comments", 0) / max(video_data.get("views", 1), 1) * self.content_parameters["engagement_metrics"]["comments_to_views"] +
                video_data.get("shares", 0) / max(video_data.get("views", 1), 1) * self.content_parameters["engagement_metrics"]["shares_to_views"]
            ) / 3
            scores.append(engagement_score * self.content_parameters["engagement_metrics"]["weight"])
            
            # Monetization score
            monetization_score = (
                video_data.get("ad_revenue", 0) / max(video_data.get("views", 1), 1) * self.content_parameters["monetization"]["cpm_rate"] +
                video_data.get("sponsorship_revenue", 0) / max(video_data.get("views", 1), 1) * self.content_parameters["monetization"]["sponsorship_rate"] +
                video_data.get("affiliate_revenue", 0) / max(video_data.get("views", 1), 1) * self.content_parameters["monetization"]["affiliate_rate"]
            ) / 3
            scores.append(monetization_score * self.content_parameters["monetization"]["weight"])
            
            # Growth score
            growth_score = (
                video_data.get("new_subscribers", 0) / max(video_data.get("views", 1), 1) * self.content_parameters["growth_metrics"]["subscriber_conversion"] +
                video_data.get("retention_rate", 0) / self.content_parameters["growth_metrics"]["retention_rate"]
            ) / 2
            scores.append(growth_score * self.content_parameters["growth_metrics"]["weight"])
            
            return sum(scores)
            
        except Exception as e:
            logger.error(f"Error calculating performance score: {str(e)}")
            raise
    
    def _generate_recommendations(self, video_data: Dict, performance_score: float) -> List[Dict]:
        """Generate content optimization recommendations."""
        try:
            recommendations = []
            
            # Video length recommendations
            if abs(video_data.get("duration", 0) - self.content_parameters["video_length"]["optimal"]) > 2:
                recommendations.append({
                    "aspect": "video_length",
                    "current": video_data.get("duration", 0),
                    "recommended": self.content_parameters["video_length"]["optimal"],
                    "impact": "High",
                    "reason": "Optimal video length for maximum engagement and monetization"
                })
            
            # Engagement recommendations
            if video_data.get("likes", 0) / max(video_data.get("views", 1), 1) < self.content_parameters["engagement_metrics"]["likes_to_views"]:
                recommendations.append({
                    "aspect": "engagement",
                    "metric": "likes",
                    "current": video_data.get("likes", 0) / max(video_data.get("views", 1), 1),
                    "target": self.content_parameters["engagement_metrics"]["likes_to_views"],
                    "impact": "Medium",
                    "reason": "Increase like-to-view ratio for better algorithm ranking"
                })
            
            # Monetization recommendations
            if video_data.get("ad_revenue", 0) / max(video_data.get("views", 1), 1) < self.content_parameters["monetization"]["cpm_rate"]:
                recommendations.append({
                    "aspect": "monetization",
                    "metric": "ad_revenue",
                    "current": video_data.get("ad_revenue", 0) / max(video_data.get("views", 1), 1),
                    "target": self.content_parameters["monetization"]["cpm_rate"],
                    "impact": "High",
                    "reason": "Optimize ad placement and content for higher CPM"
                })
            
            # Growth recommendations
            if video_data.get("new_subscribers", 0) / max(video_data.get("views", 1), 1) < self.content_parameters["growth_metrics"]["subscriber_conversion"]:
                recommendations.append({
                    "aspect": "growth",
                    "metric": "subscriber_conversion",
                    "current": video_data.get("new_subscribers", 0) / max(video_data.get("views", 1), 1),
                    "target": self.content_parameters["growth_metrics"]["subscriber_conversion"],
                    "impact": "High",
                    "reason": "Improve call-to-action and value proposition for better subscriber conversion"
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            raise
    
    def _predict_growth(self, video_data: Dict, recommendations: List[Dict]) -> Dict:
        """Predict potential growth based on current performance and recommendations."""
        try:
            current_metrics = {
                "views": video_data.get("views", 0),
                "subscribers": video_data.get("subscribers", 0),
                "revenue": video_data.get("total_revenue", 0)
            }
            
            # Calculate improvement factors based on recommendations
            improvement_factors = {
                "views": 1.0,
                "subscribers": 1.0,
                "revenue": 1.0
            }
            
            for rec in recommendations:
                if rec["impact"] == "High":
                    if rec["aspect"] == "video_length":
                        improvement_factors["views"] *= 1.2
                    elif rec["aspect"] == "engagement":
                        improvement_factors["views"] *= 1.15
                        improvement_factors["subscribers"] *= 1.1
                    elif rec["aspect"] == "monetization":
                        improvement_factors["revenue"] *= 1.25
                    elif rec["aspect"] == "growth":
                        improvement_factors["subscribers"] *= 1.2
            
            # Predict next 30 days growth
            predicted_growth = {
                "views": current_metrics["views"] * improvement_factors["views"],
                "subscribers": current_metrics["subscribers"] * improvement_factors["subscribers"],
                "revenue": current_metrics["revenue"] * improvement_factors["revenue"]
            }
            
            return {
                "current": current_metrics,
                "predicted": predicted_growth,
                "improvement_factors": improvement_factors
            }
            
        except Exception as e:
            logger.error(f"Error predicting growth: {str(e)}")
            raise
    
    def optimize_content_strategy(self, channel_data: Dict) -> Dict:
        """
        Optimize overall content strategy based on channel performance.
        
        Args:
            channel_data (Dict): Channel performance data
            
        Returns:
            Dict: Optimized content strategy
        """
        try:
            # Analyze best performing content
            best_performing = self._analyze_best_performing(channel_data)
            
            # Generate content calendar
            content_calendar = self._generate_content_calendar(channel_data, best_performing)
            
            # Optimize posting schedule
            posting_schedule = self._optimize_posting_schedule(channel_data)
            
            return {
                "best_performing_content": best_performing,
                "content_calendar": content_calendar,
                "posting_schedule": posting_schedule
            }
            
        except Exception as e:
            logger.error(f"Error optimizing content strategy: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error optimizing strategy: {str(e)}"
            )
    
    def _analyze_best_performing(self, channel_data: Dict) -> Dict:
        """Analyze best performing content to identify patterns."""
        try:
            videos = channel_data.get("videos", [])
            if not videos:
                return {}
            
            # Calculate performance scores for all videos
            video_scores = []
            for video in videos:
                score = self._calculate_performance_score(video)
                video_scores.append((video, score))
            
            # Sort by score
            video_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Analyze top performing videos
            top_videos = video_scores[:5]
            patterns = {
                "average_duration": sum(v[0].get("duration", 0) for v in top_videos) / len(top_videos),
                "common_topics": self._extract_common_topics([v[0] for v in top_videos]),
                "best_posting_times": self._extract_best_posting_times([v[0] for v in top_videos]),
                "engagement_patterns": self._analyze_engagement_patterns([v[0] for v in top_videos])
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing best performing content: {str(e)}")
            raise
    
    def _generate_content_calendar(self, channel_data: Dict, best_performing: Dict) -> List[Dict]:
        """Generate optimized content calendar."""
        try:
            calendar = []
            current_date = datetime.now()
            
            # Generate 30 days of content
            for i in range(30):
                content_day = {
                    "date": (current_date + timedelta(days=i)).isoformat(),
                    "recommended_topics": self._generate_topic_suggestions(best_performing),
                    "optimal_duration": best_performing.get("average_duration", 10),
                    "posting_time": best_performing.get("best_posting_times", ["18:00"])[0],
                    "content_type": self._determine_content_type(i, best_performing)
                }
                calendar.append(content_day)
            
            return calendar
            
        except Exception as e:
            logger.error(f"Error generating content calendar: {str(e)}")
            raise
    
    def _optimize_posting_schedule(self, channel_data: Dict) -> Dict:
        """Optimize posting schedule based on audience behavior."""
        try:
            # Analyze audience activity patterns
            activity_patterns = self._analyze_audience_activity(channel_data)
            
            # Determine optimal posting times
            optimal_times = self._determine_optimal_times(activity_patterns)
            
            # Generate weekly schedule
            weekly_schedule = {
                "monday": optimal_times[0],
                "tuesday": optimal_times[1],
                "wednesday": optimal_times[2],
                "thursday": optimal_times[3],
                "friday": optimal_times[4],
                "saturday": optimal_times[5],
                "sunday": optimal_times[6]
            }
            
            return weekly_schedule
            
        except Exception as e:
            logger.error(f"Error optimizing posting schedule: {str(e)}")
            raise

# Initialize optimizer
content_strategy_optimizer = ContentStrategyOptimizer()

@router.post("/analyze-content", response_model=APIResponse)
async def analyze_content_endpoint(video_data: Dict):
    """
    Analyze video content performance and provide optimization recommendations.
    
    Args:
        video_data (Dict): Video performance data
        
    Returns:
        APIResponse: Analysis results
    """
    try:
        analysis = content_strategy_optimizer.analyze_content_performance(video_data)
        
        return APIResponse(
            status="success",
            data=analysis,
            message="Content analysis completed successfully"
        )
        
    except Exception as e:
        logger.error(f"Error analyzing content: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing content: {str(e)}"
        )

@router.post("/optimize-strategy", response_model=APIResponse)
async def optimize_strategy_endpoint(channel_data: Dict):
    """
    Optimize overall content strategy.
    
    Args:
        channel_data (Dict): Channel performance data
        
    Returns:
        APIResponse: Optimized strategy
    """
    try:
        strategy = content_strategy_optimizer.optimize_content_strategy(channel_data)
        
        return APIResponse(
            status="success",
            data=strategy,
            message="Content strategy optimized successfully"
        )
        
    except Exception as e:
        logger.error(f"Error optimizing strategy: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error optimizing strategy: {str(e)}"
        ) 
