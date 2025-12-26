"""
Advanced Analytics Engine - Main orchestrator for complex analytics operations.
Integrates all advanced analytics components and provides unified interface.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

from .advanced_analytics_helpers import AdvancedAnalyticsHelper, PerformancePredictor
from .analytics_engine import AnalyticsEngine
from ..database import get_all_ideas, get_idea_by_id
from ..utils import log_execution

logger = logging.getLogger(__name__)

class AdvancedAnalyticsEngine:
    """
    Advanced Analytics Engine that provides comprehensive analytics capabilities
    including predictive modeling, deep insights, and strategic recommendations.
    """
    
    def __init__(self):
        self.analytics_helper = AdvancedAnalyticsHelper()
        self.performance_predictor = PerformancePredictor()
        self.base_analytics = AnalyticsEngine()
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache TTL
    
    async def generate_comprehensive_report(self, 
                                          channel_data: Optional[Dict[str, Any]] = None,
                                          include_predictions: bool = True,
                                          include_competitive_analysis: bool = True,
                                          timeframe_days: int = 90) -> Dict[str, Any]:
        """
        Generate comprehensive analytics report with all advanced features.
        
        Args:
            channel_data: Optional channel data, if not provided will fetch from database
            include_predictions: Whether to include predictive analytics
            include_competitive_analysis: Whether to include competitive analysis
            timeframe_days: Timeframe for analysis in days
            
        Returns:
            Dict containing comprehensive analytics report
        """
        try:
            logger.info("Generating comprehensive analytics report")
            
            # Fetch data if not provided
            if not channel_data:
                channel_data = await self._fetch_channel_data(timeframe_days)
            
            videos = channel_data.get("videos", [])
            if not videos:
                return {"error": "No video data available for analysis"}
            
            # Initialize report structure
            report = {
                "report_metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "timeframe_days": timeframe_days,
                    "videos_analyzed": len(videos),
                    "analysis_depth": "comprehensive"
                },
                "executive_summary": {},
                "performance_analytics": {},
                "content_insights": {},
                "audience_analytics": {},
                "revenue_analysis": {},
                "growth_analysis": {},
                "predictive_insights": {},
                "competitive_intelligence": {},
                "strategic_recommendations": {},
                "action_items": []
            }
            
            # Generate executive summary
            report["executive_summary"] = await self._generate_executive_summary(videos)
            
            # Core performance analytics
            report["performance_analytics"] = await self._generate_performance_analytics(videos)
            
            # Content insights
            report["content_insights"] = await self._generate_content_insights(videos)
            
            # Audience analytics
            report["audience_analytics"] = await self._generate_audience_analytics(videos)
            
            # Revenue analysis
            report["revenue_analysis"] = await self._generate_revenue_analysis(videos)
            
            # Growth analysis
            report["growth_analysis"] = await self._generate_growth_analysis(videos)
            
            # Predictive insights (if requested)
            if include_predictions:
                report["predictive_insights"] = await self._generate_predictive_insights(videos, channel_data)
            
            # Competitive intelligence (if requested)
            if include_competitive_analysis:
                report["competitive_intelligence"] = await self._generate_competitive_intelligence(videos)
            
            # Strategic recommendations
            report["strategic_recommendations"] = await self._generate_strategic_recommendations(report)
            
            # Action items
            report["action_items"] = await self._generate_action_items(report)
            
            # Log successful report generation
            log_execution(
                "comprehensive_analytics_report",
                "success",
                {
                    "videos_analyzed": len(videos),
                    "timeframe_days": timeframe_days,
                    "report_sections": len([k for k, v in report.items() if v and k != "report_metadata"])
                }
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {str(e)}")
            return {"error": f"Failed to generate comprehensive report: {str(e)}"}
    
    async def analyze_content_performance_deep(self, video_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Perform deep content performance analysis with advanced metrics.
        
        Args:
            video_ids: Optional list of specific video IDs to analyze
            
        Returns:
            Dict containing deep performance analysis
        """
        try:
            # Fetch video data
            if video_ids:
                videos = []
                for video_id in video_ids:
                    video = get_idea_by_id(video_id)
                    if video:
                        videos.append(video)
            else:
                videos = get_all_ideas()
            
            if not videos:
                return {"error": "No videos found for analysis"}
            
            # Perform deep analysis
            analysis = {
                "performance_overview": await self._analyze_performance_overview(videos),
                "content_quality_analysis": await self._analyze_content_quality(videos),
                "engagement_deep_dive": await self._analyze_engagement_patterns(videos),
                "retention_analysis": self.analytics_helper.analyze_audience_retention(videos),
                "viral_potential_analysis": self.analytics_helper.analyze_viral_potential(videos),
                "lifecycle_analysis": self.analytics_helper.analyze_content_lifecycle(videos),
                "optimization_opportunities": await self._identify_optimization_opportunities(videos),
                "performance_benchmarks": await self._calculate_performance_benchmarks(videos)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in deep content performance analysis: {str(e)}")
            return {"error": str(e)}
    
    async def predict_future_performance(self, 
                                       prediction_timeframe_months: int = 6,
                                       content_plan: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Predict future channel and content performance.
        
        Args:
            prediction_timeframe_months: Months to predict into the future
            content_plan: Optional planned content for prediction
            
        Returns:
            Dict containing performance predictions
        """
        try:
            # Fetch historical data
            historical_data = get_all_ideas()
            if len(historical_data) < 3:
                return {"error": "Insufficient historical data for predictions"}
            
            # Get current metrics
            current_metrics = await self._calculate_current_metrics(historical_data)
            
            # Generate predictions
            predictions = {
                "prediction_metadata": {
                    "timeframe_months": prediction_timeframe_months,
                    "historical_data_points": len(historical_data),
                    "prediction_confidence": self._assess_prediction_confidence(historical_data)
                },
                "channel_growth_prediction": await self.performance_predictor.predict_channel_growth(
                    current_metrics, historical_data, prediction_timeframe_months
                ),
                "revenue_predictions": {},
                "content_performance_predictions": [],
                "milestone_predictions": {},
                "risk_assessment": {}
            }
            
            # Revenue predictions
            if content_plan:
                market_data = await self._get_market_data()
                predictions["revenue_predictions"] = await self.performance_predictor.predict_revenue_potential(
                    content_plan, market_data
                )
            
            # Individual content predictions
            if content_plan:
                for content_item in content_plan:
                    content_prediction = await self.performance_predictor.predict_video_performance(
                        content_item, historical_data
                    )
                    predictions["content_performance_predictions"].append(content_prediction)
            
            # Milestone predictions
            predictions["milestone_predictions"] = await self._predict_growth_milestones(
                current_metrics, historical_data, prediction_timeframe_months
            )
            
            # Risk assessment
            predictions["risk_assessment"] = await self._assess_prediction_risks(
                predictions, historical_data
            )
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error predicting future performance: {str(e)}")
            return {"error": str(e)}
    
    async def generate_competitive_analysis(self, 
                                          competitor_data: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Generate comprehensive competitive analysis.
        
        Args:
            competitor_data: Optional competitor data, if not provided will simulate
            
        Returns:
            Dict containing competitive analysis
        """
        try:
            # Get own channel data
            own_videos = get_all_ideas()
            if not own_videos:
                return {"error": "No channel data available for competitive analysis"}
            
            # Simulate competitor data if not provided
            if not competitor_data:
                competitor_data = await self._simulate_competitor_data()
            
            # Perform competitive analysis
            analysis = self.analytics_helper.analyze_competitive_landscape(own_videos, competitor_data)
            
            # Add strategic insights
            analysis["strategic_insights"] = await self._generate_competitive_insights(analysis, own_videos)
            analysis["market_positioning"] = await self._analyze_market_positioning(own_videos, competitor_data)
            analysis["competitive_advantages"] = await self._identify_competitive_advantages(own_videos, analysis)
            analysis["threat_assessment"] = await self._assess_competitive_threats(analysis, competitor_data)
            analysis["opportunity_mapping"] = await self._map_competitive_opportunities(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error generating competitive analysis: {str(e)}")
            return {"error": str(e)}
    
    async def optimize_content_strategy(self, 
                                      current_strategy: Dict[str, Any],
                                      optimization_goals: List[str]) -> Dict[str, Any]:
        """
        Optimize content strategy based on analytics insights.
        
        Args:
            current_strategy: Current content strategy
            optimization_goals: List of optimization goals
            
        Returns:
            Dict containing optimized strategy recommendations
        """
        try:
            # Analyze current performance
            videos = get_all_ideas()
            performance_analysis = await self.analyze_content_performance_deep()
            
            # Generate optimization recommendations
            optimization = {
                "current_strategy_analysis": await self._analyze_current_strategy(current_strategy, videos),
                "goal_alignment_assessment": await self._assess_goal_alignment(optimization_goals, performance_analysis),
                "optimization_recommendations": await self._generate_optimization_recommendations(
                    current_strategy, optimization_goals, performance_analysis
                ),
                "implementation_roadmap": await self._create_implementation_roadmap(optimization_goals),
                "success_metrics": await self._define_success_metrics(optimization_goals),
                "risk_mitigation": await self._identify_strategy_risks(current_strategy, optimization_goals)
            }
            
            return optimization
            
        except Exception as e:
            logger.error(f"Error optimizing content strategy: {str(e)}")
            return {"error": str(e)}
    
    # Private helper methods
    async def _fetch_channel_data(self, timeframe_days: int) -> Dict[str, Any]:
        """Fetch channel data for specified timeframe."""
        videos = get_all_ideas()
        
        # Filter by timeframe if needed
        cutoff_date = datetime.utcnow() - timedelta(days=timeframe_days)
        filtered_videos = []
        
        for video in videos:
            try:
                created_at = datetime.fromisoformat(video.get("created_at", "").replace('Z', '+00:00'))
                if created_at >= cutoff_date:
                    filtered_videos.append(video)
            except:
                # Include videos without valid dates
                filtered_videos.append(video)
        
        return {
            "videos": filtered_videos,
            "total_videos": len(videos),
            "timeframe_videos": len(filtered_videos),
            "channel_metadata": {
                "analysis_date": datetime.utcnow().isoformat(),
                "timeframe_days": timeframe_days
            }
        }
    
    async def _generate_executive_summary(self, videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate executive summary of channel performance."""
        if not videos:
            return {"error": "No videos to analyze"}
        
        # Calculate key metrics
        total_views = sum(v.get("expected_views", 0) for v in videos)
        avg_performance = statistics.mean([v.get("performance_score", 0) for v in videos if v.get("performance_score")])
        
        # Identify top performers
        top_videos = sorted(videos, key=lambda x: x.get("expected_views", 0), reverse=True)[:3]
        
        # Calculate growth trend
        growth_trend = await self._calculate_growth_trend(videos)
        
        return {
            "key_metrics": {
                "total_videos": len(videos),
                "total_views": total_views,
                "average_performance_score": round(avg_performance, 1),
                "average_views_per_video": round(total_views / len(videos), 0) if videos else 0
            },
            "performance_summary": {
                "overall_rating": self._rate_performance(avg_performance),
                "growth_trend": growth_trend,
                "top_performing_videos": [
                    {
                        "title": v.get("title", "Unknown"),
                        "views": v.get("expected_views", 0),
                        "performance_score": v.get("performance_score", 0)
                    }
                    for v in top_videos
                ]
            },
            "key_insights": await self._generate_key_insights(videos),
            "priority_recommendations": await self._generate_priority_recommendations(videos)
        }
    
    async def _generate_performance_analytics(self, videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate detailed performance analytics."""
        return {
            "overall_performance": await self._calculate_overall_performance(videos),
            "performance_distribution": await self._analyze_performance_distribution(videos),
            "category_performance": await self._analyze_category_performance(videos),
            "temporal_performance": await self._analyze_temporal_performance(videos),
            "performance_correlations": await self._analyze_performance_correlations(videos)
        }
    
    async def _generate_content_insights(self, videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate content-specific insights."""
        return {
            "content_themes": await self._analyze_content_themes(videos),
            "title_analysis": await self._analyze_title_patterns(videos),
            "content_length_analysis": await self._analyze_content_length_impact(videos),
            "topic_performance": await self._analyze_topic_performance(videos),
            "content_gaps": await self._identify_content_gaps(videos)
        }
    
    async def _generate_audience_analytics(self, videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate audience analytics."""
        return {
            "engagement_patterns": await self._analyze_engagement_patterns(videos),
            "audience_preferences": await self._analyze_audience_preferences(videos),
            "retention_insights": self.analytics_helper.analyze_audience_retention(videos),
            "audience_growth": await self._analyze_audience_growth(videos)
        }
    
    async def _generate_revenue_analysis(self, videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate revenue analysis."""
        return {
            "revenue_overview": await self._calculate_revenue_overview(videos),
            "revenue_by_content": await self._analyze_revenue_by_content(videos),
            "monetization_efficiency": await self._analyze_monetization_efficiency(videos),
            "revenue_optimization": await self._identify_revenue_optimization_opportunities(videos)
        }
    
    async def _generate_growth_analysis(self, videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate growth analysis."""
        return {
            "growth_metrics": await self._calculate_growth_metrics(videos),
            "growth_drivers": await self._identify_growth_drivers(videos),
            "growth_bottlenecks": await self._identify_growth_bottlenecks(videos),
            "growth_opportunities": await self._identify_growth_opportunities(videos)
        }
    
    async def _generate_predictive_insights(self, videos: List[Dict[str, Any]], channel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate predictive insights."""
        current_metrics = await self._calculate_current_metrics(videos)
        
        return {
            "performance_predictions": await self.performance_predictor.predict_channel_growth(
                current_metrics, videos, 6
            ),
            "trend_predictions": await self._predict_content_trends(videos),
            "growth_projections": await self._project_growth_scenarios(videos),
            "risk_predictions": await self._predict_performance_risks(videos)
        }
    
    async def _generate_competitive_intelligence(self, videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate competitive intelligence."""
        competitor_data = await self._simulate_competitor_data()
        
        return self.analytics_helper.analyze_competitive_landscape(videos, competitor_data)
    
    async def _generate_strategic_recommendations(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Generate strategic recommendations based on full report."""
        recommendations = {
            "content_strategy": [],
            "growth_strategy": [],
            "monetization_strategy": [],
            "audience_strategy": [],
            "competitive_strategy": []
        }
        
        # Content strategy recommendations
        performance_analytics = report.get("performance_analytics", {})
        if performance_analytics.get("overall_performance", {}).get("average_score", 0) < 60:
            recommendations["content_strategy"].append({
                "priority": "high",
                "recommendation": "Focus on improving content quality and production value",
                "rationale": "Below-average performance scores indicate quality improvement needed"
            })
        
        # Growth strategy recommendations
        growth_analysis = report.get("growth_analysis", {})
        growth_rate = growth_analysis.get("growth_metrics", {}).get("monthly_growth_rate", 0)
        if growth_rate < 0.05:  # Less than 5% monthly growth
            recommendations["growth_strategy"].append({
                "priority": "high",