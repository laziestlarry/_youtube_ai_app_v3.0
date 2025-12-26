from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional, Any
import logging
from datetime import datetime, timedelta
from backend.models import APIResponse
from database import log_execution
import json
import numpy as np
from collections import defaultdict
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()

class AnalyticsEngine:
    def __init__(self):
        self.metrics = defaultdict(list)
        self.trends = {}
        self.predictions = {}
        self.tracking_config = {}
        self.monitoring_config = {}
    
    async def configure_tracking(self, config: Dict[str, Any]) -> None:
        """
        Configure analytics tracking settings.
        
        Args:
            config (Dict[str, Any]): Tracking configuration
        """
        self.tracking_config = config
        logger.info(f"Analytics tracking configured: {config}")
    
    async def setup_performance_monitoring(self) -> None:
        """
        Set up performance monitoring system.
        """
        self.monitoring_config = {
            "enabled": True,
            "metrics": ["views", "engagement", "revenue", "growth"],
            "alert_thresholds": {
                "views": 1000,
                "engagement": 0.05,
                "revenue": 100,
                "growth": 0.1
            }
        }
        logger.info("Performance monitoring system initialized")
    
    def calculate_engagement_score(self, views: int, likes: int, comments: int, shares: int) -> float:
        """
        Calculate engagement score based on various metrics.
        
        Args:
            views (int): Number of views
            likes (int): Number of likes
            comments (int): Number of comments
            shares (int): Number of shares
            
        Returns:
            float: Engagement score (0-100)
        """
        if views == 0:
            return 0.0
            
        engagement_rate = (likes + comments * 2 + shares * 3) / views
        return min(100, max(0, engagement_rate * 1000))
    
    def analyze_trends(self, data: List[Dict[str, any]]) -> Dict[str, any]:
        """
        Analyze trends in video performance data.
        
        Args:
            data (List[Dict[str, any]]): List of video performance data
            
        Returns:
            Dict[str, any]: Trend analysis results
        """
        trends = {
            "views": self._calculate_growth_rate([d["views"] for d in data]),
            "engagement": self._calculate_growth_rate([d["engagement_score"] for d in data]),
            "best_performing_categories": self._analyze_categories(data),
            "optimal_posting_times": self._analyze_posting_times(data)
        }
        
        return trends
    
    def predict_performance(self, video_data: Dict[str, any]) -> Dict[str, any]:
        """
        Predict video performance based on historical data.
        
        Args:
            video_data (Dict[str, any]): Video metadata and content
            
        Returns:
            Dict[str, any]: Performance predictions
        """
        predictions = {
            "estimated_views": self._predict_views(video_data),
            "estimated_engagement": self._predict_engagement(video_data),
            "optimal_posting_time": self._predict_posting_time(video_data),
            "content_recommendations": self._generate_recommendations(video_data)
        }
        
        return predictions
    
    def _calculate_growth_rate(self, values: List[float]) -> float:
        """Calculate growth rate from a list of values."""
        if len(values) < 2:
            return 0.0
        return ((values[-1] - values[0]) / values[0]) * 100
    
    def _analyze_categories(self, data: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """Analyze best performing categories."""
        category_performance = defaultdict(lambda: {"views": 0, "engagement": 0, "count": 0})
        
        for video in data:
            category = video.get("category", "unknown")
            category_performance[category]["views"] += video["views"]
            category_performance[category]["engagement"] += video["engagement_score"]
            category_performance[category]["count"] += 1
        
        return [
            {
                "category": cat,
                "avg_views": perf["views"] / perf["count"],
                "avg_engagement": perf["engagement"] / perf["count"]
            }
            for cat, perf in sorted(
                category_performance.items(),
                key=lambda x: x[1]["engagement"] / x[1]["count"],
                reverse=True
            )[:5]
        ]
    
    def _analyze_posting_times(self, data: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """Analyze optimal posting times."""
        time_performance = defaultdict(lambda: {"views": 0, "engagement": 0, "count": 0})
        
        for video in data:
            hour = video.get("posted_at", datetime.now()).hour
            time_performance[hour]["views"] += video["views"]
            time_performance[hour]["engagement"] += video["engagement_score"]
            time_performance[hour]["count"] += 1
        
        return [
            {
                "hour": hour,
                "avg_views": perf["views"] / perf["count"],
                "avg_engagement": perf["engagement"] / perf["count"]
            }
            for hour, perf in sorted(
                time_performance.items(),
                key=lambda x: x[1]["engagement"] / x[1]["count"],
                reverse=True
            )[:5]
        ]
    
    def _predict_views(self, video_data: Dict[str, any]) -> Dict[str, any]:
        """Predict video views."""
        # Simple prediction based on category and time
        base_views = {
            "tech": 1000,
            "gaming": 2000,
            "education": 800,
            "business": 1500
        }.get(video_data.get("category", "other"), 500)
        
        return {
            "min": int(base_views * 0.5),
            "expected": base_views,
            "max": int(base_views * 2)
        }
    
    def _predict_engagement(self, video_data: Dict[str, any]) -> Dict[str, any]:
        """Predict video engagement."""
        # Simple prediction based on content length and category
        base_engagement = {
            "tech": 0.05,
            "gaming": 0.08,
            "education": 0.04,
            "business": 0.06
        }.get(video_data.get("category", "other"), 0.03)
        
        return {
            "min": base_engagement * 0.5,
            "expected": base_engagement,
            "max": base_engagement * 2
        }
    
    def _predict_posting_time(self, video_data: Dict[str, any]) -> List[Dict[str, any]]:
        """Predict optimal posting times."""
        return [
            {"hour": 12, "day": "Monday"},
            {"hour": 15, "day": "Wednesday"},
            {"hour": 18, "day": "Friday"}
        ]
    
    def _generate_recommendations(self, video_data: Dict[str, any]) -> List[str]:
        """Generate content recommendations."""
        recommendations = []
        
        # Length recommendations
        if video_data.get("duration", 0) < 300:
            recommendations.append("Consider making longer videos (5-10 minutes) for better engagement")
        elif video_data.get("duration", 0) > 1800:
            recommendations.append("Consider breaking down long videos into series for better retention")
        
        # Category-specific recommendations
        category_recommendations = {
            "tech": "Include technical demonstrations and code examples",
            "gaming": "Add gameplay highlights and commentary",
            "education": "Include visual aids and examples",
            "business": "Add case studies and real-world examples"
        }
        
        if video_data.get("category") in category_recommendations:
            recommendations.append(category_recommendations[video_data["category"]])
        
        return recommendations

# Initialize analytics engine
analytics_engine = AnalyticsEngine()

class PerformanceAnalysis(BaseModel):
    score: float
    recommendations: List[str]

class PerformancePrediction(BaseModel):
    predicted_views: int
    confidence: float

class EngagementMetrics(BaseModel):
    engagement_score: float
    metrics: Dict[str, float]

class ContentInsights(BaseModel):
    insights: List[str]
    trends: Dict[str, Any]

class StrategyOptimization(BaseModel):
    recommendations: List[str]
    metrics: Dict[str, Any]

class AnalyticsReport(BaseModel):
    report: Dict[str, Any]
    timestamp: str

class MetricsTracking(BaseModel):
    status: str
    metrics: Dict[str, Any]

class DataExport(BaseModel):
    data: Dict[str, Any]
    format: str

class BatchProcessResult(BaseModel):
    status: str
    results: List[Dict[str, Any]]

class HealthStatus(BaseModel):
    status: str
    version: str
    timestamp: str

@router.post("/api/v1/analyze-performance", response_model=PerformanceAnalysis)
async def analyze_performance_endpoint(data: List[Dict[str, Any]]):
    try:
        score, recommendations = analytics_engine.analyze_performance(data)
        return PerformanceAnalysis(score=score, recommendations=recommendations)
    except Exception as e:
        logger.error(f"Error analyzing performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/v1/predict-performance", response_model=PerformancePrediction)
async def predict_performance_endpoint(data: Dict[str, Any]):
    try:
        predicted_views, confidence = analytics_engine.predict_performance(data)
        return PerformancePrediction(predicted_views=predicted_views, confidence=confidence)
    except Exception as e:
        logger.error(f"Error predicting performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/v1/calculate-engagement", response_model=EngagementMetrics)
async def calculate_engagement_endpoint(data: Dict[str, Any]):
    try:
        engagement_score, metrics = analytics_engine.calculate_engagement(data)
        return EngagementMetrics(engagement_score=engagement_score, metrics=metrics)
    except Exception as e:
        logger.error(f"Error calculating engagement: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/v1/generate-insights", response_model=ContentInsights)
async def generate_insights_endpoint(data: List[Dict[str, Any]]):
    try:
        insights, trends = analytics_engine.generate_insights(data)
        return ContentInsights(insights=insights, trends=trends)
    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/v1/optimize-strategy", response_model=StrategyOptimization)
async def optimize_strategy_endpoint(data: Dict[str, Any]):
    try:
        recommendations, metrics = analytics_engine.optimize_strategy(data)
        return StrategyOptimization(recommendations=recommendations, metrics=metrics)
    except Exception as e:
        logger.error(f"Error optimizing strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/v1/generate-report", response_model=AnalyticsReport)
async def generate_report_endpoint(data: Dict[str, Any]):
    try:
        report = analytics_engine.generate_report(data)
        return AnalyticsReport(report=report, timestamp=datetime.utcnow().isoformat())
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/v1/track-metrics", response_model=MetricsTracking)
async def track_metrics_endpoint(data: Dict[str, Any]):
    try:
        status, metrics = analytics_engine.track_metrics(data)
        return MetricsTracking(status=status, metrics=metrics)
    except Exception as e:
        logger.error(f"Error tracking metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/v1/export-data", response_model=DataExport)
async def export_data_endpoint(data: Dict[str, Any], format: str = "json"):
    try:
        exported_data = analytics_engine.export_data(data, format)
        return DataExport(data=exported_data, format=format)
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/v1/batch-process", response_model=BatchProcessResult)
async def batch_process_endpoint(data: List[Dict[str, Any]]):
    try:
        status, results = analytics_engine.batch_process(data)
        return BatchProcessResult(status=status, results=results)
    except Exception as e:
        logger.error(f"Error in batch processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/health", response_model=HealthStatus)
async def health_check():
    return HealthStatus(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat()
    ) 