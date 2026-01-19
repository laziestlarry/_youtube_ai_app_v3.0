import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import json

from ..database import get_db_connection
from backend.utils.logging_utils import log_execution

logger = logging.getLogger(__name__)

class AdvancedAnalyticsEngine:
    """
    Advanced analytics engine for comprehensive YouTube channel data analysis.

    This engine provides deep insights into channel health, content performance,
    audience behavior, growth patterns, monetization efficiency, and competitive
    landscape. It leverages statistical methods and machine learning techniques
    to generate actionable recommendations for channel optimization and revenue
    maximization.

    Attributes:
        scaler (StandardScaler): Scikit-learn scaler for feature normalization.
        anomaly_detector (IsolationForest): Model for detecting anomalies in data.
        clustering_model (KMeans): Model for clustering content or audience segments.
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.clustering_model = KMeans(n_clusters=5, random_state=42)
        self.pca_model = PCA(n_components=2)
        
        # Cache for processed data
        self.data_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
    async def comprehensive_channel_analysis(
        self, 
        channel_data: Dict[str, Any],
        time_period: int = 30
    ) -> Dict[str, Any]:
        """
        Perform comprehensive channel analysis with advanced metrics.
        
        Args:
            channel_data (Dict[str, Any]): A dictionary containing structured channel data.
                Expected keys might include 'videos' (list of video dicts),
                'subscriber_history', 'demographics', etc.
                Each video dict should contain metrics like 'views', 'engagement_rate',
                'retention_rate', 'published_at', 'category', 'ad_revenue', etc.
            time_period (int, optional): The analysis period in days, looking back from
                the most recent data. Defaults to 30.
            
        Returns:
            Dict[str, Any]: A dictionary containing comprehensive analysis results,
            structured into sections like 'channel_health', 'content_performance', etc.
        """
        if not channel_data or not isinstance(channel_data, dict):
            raise ValueError("channel_data must be a non-empty dictionary.")
        try:
            analysis_results = {
                "channel_health": {},
                "content_performance": {},
                "audience_insights": {},
                "growth_analysis": {},
                "monetization_analysis": {},
                "competitive_analysis": {},
                "predictive_insights": {},
                "recommendations": []
            }
            
            # Channel Health Analysis
            analysis_results["channel_health"] = await self._analyze_channel_health(channel_data)
            
            # Content Performance Analysis
            analysis_results["content_performance"] = await self._analyze_content_performance(channel_data)
            
            # Audience Insights
            analysis_results["audience_insights"] = await self._analyze_audience_behavior(channel_data)
            
            # Growth Analysis
            analysis_results["growth_analysis"] = await self._analyze_growth_patterns(channel_data, time_period)
            
            # Monetization Analysis
            analysis_results["monetization_analysis"] = await self._analyze_monetization_efficiency(channel_data)
            
            # Competitive Analysis
            analysis_results["competitive_analysis"] = await self._perform_competitive_analysis(channel_data)
            
            # Predictive Insights
            analysis_results["predictive_insights"] = await self._generate_predictive_insights(channel_data)
            
            # Generate Recommendations
            analysis_results["recommendations"] = await self._generate_comprehensive_recommendations(analysis_results)
            
            # Log analysis execution
            log_execution(
                "comprehensive_channel_analysis",
                "success",
                {
                    "time_period": time_period,
                    "metrics_analyzed": len(analysis_results),
                    "recommendations_count": len(analysis_results["recommendations"])
                }
            )
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error in comprehensive channel analysis: {str(e)}")
            raise
    
    async def _analyze_channel_health(self, channel_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze overall channel health metrics.

        Calculates a weighted health score based on average views, engagement,
        retention, and content consistency.

        Args:
            channel_data (Dict[str, Any]): Channel data containing a list of videos.

        Returns:
            Dict[str, Any]: Analysis of channel health, including score, status, and trends.
        """
        try:
            videos = channel_data.get("videos", [])
            if not videos:
                return {"health_score": 0, "status": "insufficient_data"}
            
            # Calculate health metrics
            avg_views = np.mean([v.get("views", 0) for v in videos])
            avg_engagement = np.mean([v.get("engagement_rate", 0) for v in videos])
            avg_retention = np.mean([v.get("retention_rate", 0) for v in videos])
            consistency_score = self._calculate_consistency_score(videos)
            
            # Weighted health score
            health_score = (
                (avg_views / 10000) * 0.3 +  # Views weight
                avg_engagement * 0.25 +       # Engagement weight
                avg_retention * 0.25 +        # Retention weight
                consistency_score * 0.2       # Consistency weight
            ) * 100
            
            health_score = min(100, max(0, health_score))
            
            # Determine health status
            if health_score >= 80:
                status = "excellent"
            elif health_score >= 60:
                status = "good"
            elif health_score >= 40:
                status = "fair"
            else:
                status = "poor"
            
            return {
                "health_score": round(health_score, 2),
                "status": status,
                "metrics": {
                    "average_views": round(avg_views, 2),
                    "average_engagement": round(avg_engagement, 4),
                    "average_retention": round(avg_retention, 4),
                    "consistency_score": round(consistency_score, 4)
                },
                "trends": self._analyze_health_trends(videos)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing channel health: {str(e)}")
            return {"health_score": 0, "status": "error", "error": str(e)}
    
    async def _analyze_content_performance(self, channel_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze content performance patterns, including clustering and lifecycle.

        Identifies top-performing content, analyzes content types, optimal posting
        patterns, and content lifecycle stages.

        Args:
            channel_data (Dict[str, Any]): Channel data with video information.

        Returns:
            Dict[str, Any]: Detailed analysis of content performance.
        """
        try:
            videos = channel_data.get("videos", [])
            if not videos:
                return {"status": "insufficient_data"}
            
            # Performance clustering
            performance_clusters = self._cluster_content_performance(videos)
            
            # Best performing content analysis
            top_performers = sorted(videos, key=lambda x: x.get("views", 0), reverse=True)[:10]
            
            # Content type analysis
            content_types = self._analyze_content_types(videos)
            
            # Optimal posting analysis
            posting_patterns = self._analyze_posting_patterns(videos)
            
            # Content lifecycle analysis
            lifecycle_analysis = self._analyze_content_lifecycle(videos)
            
            return {
                "performance_clusters": performance_clusters,
                "top_performers": [
                    {
                        "title": v.get("title", ""),
                        "views": v.get("views", 0),
                        "engagement_rate": v.get("engagement_rate", 0),
                        "performance_score": self._calculate_performance_score(v)
                    }
                    for v in top_performers
                ],
                "content_types": content_types,
                "posting_patterns": posting_patterns,
                "lifecycle_analysis": lifecycle_analysis
            }
            
        except Exception as e:
            logger.error(f"Error analyzing content performance: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _analyze_audience_behavior(self, channel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze audience behavior patterns."""
        try:
            videos = channel_data.get("videos", [])
            if not videos:
                return {"status": "insufficient_data"}
            
            # Engagement patterns
            engagement_patterns = self._analyze_engagement_patterns(videos)
            
            # Audience retention analysis
            retention_analysis = self._analyze_retention_patterns(videos)
            
            # Comment sentiment analysis
            sentiment_analysis = self._analyze_comment_sentiment(videos)
            
            # Audience growth analysis
            growth_analysis = self._analyze_audience_growth(channel_data)
            
            # Demographic insights (if available)
            demographic_insights = self._analyze_demographics(channel_data)
            
            return {
                "engagement_patterns": engagement_patterns,
                "retention_analysis": retention_analysis,
                "sentiment_analysis": sentiment_analysis,
                "growth_analysis": growth_analysis,
                "demographic_insights": demographic_insights
            }
            
        except Exception as e:
            logger.error(f"Error analyzing audience behavior: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _analyze_growth_patterns(self, channel_data: Dict[str, Any], time_period: int) -> Dict[str, Any]:
        """Analyze channel growth patterns."""
        try:
            # Growth rate calculation
            growth_metrics = self._calculate_growth_metrics(channel_data, time_period)
            
            # Growth trend analysis
            trend_analysis = self._analyze_growth_trends(channel_data)
            
            # Growth acceleration/deceleration
            acceleration_analysis = self._analyze_growth_acceleration(channel_data)
            
            # Seasonal patterns
            seasonal_patterns = self._analyze_seasonal_patterns(channel_data)
            
            # Growth forecasting
            growth_forecast = self._forecast_growth(channel_data, time_period)
            
            return {
                "growth_metrics": growth_metrics,
                "trend_analysis": trend_analysis,
                "acceleration_analysis": acceleration_analysis,
                "seasonal_patterns": seasonal_patterns,
                "growth_forecast": growth_forecast
            }
            
        except Exception as e:
            logger.error(f"Error analyzing growth patterns: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _analyze_monetization_efficiency(self, channel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze monetization efficiency and opportunities."""
        try:
            videos = channel_data.get("videos", [])
            if not videos:
                return {"status": "insufficient_data"}
            
            # Revenue per view analysis
            rpv_analysis = self._analyze_revenue_per_view(videos)
            
            # Monetization channel analysis
            monetization_channels = self._analyze_monetization_channels(videos)
            
            # Revenue optimization opportunities
            optimization_opportunities = self._identify_revenue_opportunities(videos)
            
            # CPM analysis
            cpm_analysis = self._analyze_cpm_trends(videos)
            
            # Revenue forecasting
            revenue_forecast = self._forecast_revenue(videos)
            
            return {
                "rpv_analysis": rpv_analysis,
                "monetization_channels": monetization_channels,
                "optimization_opportunities": optimization_opportunities,
                "cpm_analysis": cpm_analysis,
                "revenue_forecast": revenue_forecast
            }
            
        except Exception as e:
            logger.error(f"Error analyzing monetization efficiency: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _perform_competitive_analysis(self, channel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform competitive analysis."""
        try:
            # This would typically involve external data sources
            # For now, we'll provide a framework
            
            competitive_metrics = {
                "market_position": self._estimate_market_position(channel_data),
                "content_gaps": self._identify_content_gaps(channel_data),
                "competitive_advantages": self._identify_competitive_advantages(channel_data),
                "benchmark_comparison": self._compare_to_benchmarks(channel_data)
            }
            
            return competitive_metrics
            
        except Exception as e:
            logger.error(f"Error in competitive analysis: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _generate_predictive_insights(self, channel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate predictive insights using machine learning."""
        try:
            videos = channel_data.get("videos", [])
            if len(videos) < 10:
                return {"status": "insufficient_data"}
            
            # Prepare data for ML models
            features = self._extract_features_for_prediction(videos)
            
            # Anomaly detection
            anomalies = self._detect_performance_anomalies(features)
            
            # Performance prediction
            performance_predictions = self._predict_video_performance(features)
            
            # Trend predictions
            trend_predictions = self._predict_trends(features)
            
            # Risk assessment
            risk_assessment = self._assess_channel_risks(features)
            
            return {
                "anomalies": anomalies,
                "performance_predictions": performance_predictions,
                "trend_predictions": trend_predictions,
                "risk_assessment": risk_assessment
            }
            
        except Exception as e:
            logger.error(f"Error generating predictive insights: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _generate_comprehensive_recommendations(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate comprehensive recommendations based on analysis."""
        try:
            recommendations = []
            
            # Health-based recommendations
            health_score = analysis_results.get("channel_health", {}).get("health_score", 0)
            if health_score < 60:
                recommendations.append({
                    "category": "channel_health",
                    "priority": "high",
                    "title": "Improve Channel Health",
                    "description": "Channel health score is below optimal. Focus on consistency and engagement.",
                    "actions": [
                        "Maintain regular posting schedule",
                        "Improve video thumbnails and titles",
                        "Engage more with audience in comments",
                        "Analyze top-performing content patterns"
                    ]
                })
            
            # Content performance recommendations
            content_perf = analysis_results.get("content_performance", {})
            if content_perf.get("performance_clusters"):
                recommendations.append({
                    "category": "content_optimization",
                    "priority": "medium",
                    "title": "Optimize Content Strategy",
                    "description": "Leverage insights from performance clustering to improve content strategy.",
                    "actions": [
                        "Focus on high-performing content types",
                        "Replicate successful content patterns",
                        "Experiment with underperforming categories"
                    ]
                })
            
            # Growth recommendations
            growth_analysis = analysis_results.get("growth_analysis", {})
            growth_metrics = growth_analysis.get("growth_metrics", {})
            if growth_metrics.get("growth_rate", 0) < 0.05:  # Less than 5% growth
                recommendations.append({
                    "category": "growth_acceleration",
                    "priority": "high",
                    "title": "Accelerate Channel Growth",
                    "description": "Current growth rate is below industry average.",
                    "actions": [
                        "Increase content frequency",
                        "Improve SEO optimization",
                        "Collaborate with other creators",
                        "Promote content on social media"
                    ]
                })
            
            # Monetization recommendations
            monetization = analysis_results.get("monetization_analysis", {})
            if monetization.get("optimization_opportunities"):
                recommendations.append({
                    "category": "monetization",
                    "priority": "medium",
                    "title": "Optimize Revenue Streams",
                    "description": "Multiple opportunities identified to increase revenue.",
                    "actions": [
                        "Diversify monetization channels",
                        "Optimize ad placement",
                        "Consider premium content offerings",
                        "Explore brand partnerships"
                    ]
                })
            
            # Audience engagement recommendations
            audience_insights = analysis_results.get("audience_insights", {})
            engagement_patterns = audience_insights.get("engagement_patterns", {})
            if engagement_patterns.get("average_engagement", 0) < 0.03:  # Less than 3%
                recommendations.append({
                    "category": "audience_engagement",
                    "priority": "high",
                    "title": "Boost Audience Engagement",
                    "description": "Engagement rates are below optimal levels.",
                    "actions": [
                        "Create more interactive content",
                        "Ask questions in videos",
                        "Respond to comments promptly",
                        "Use community posts effectively"
                    ]
                })
            
            # Predictive recommendations
            predictive = analysis_results.get("predictive_insights", {})
            risk_assessment = predictive.get("risk_assessment", {})
            if risk_assessment.get("risk_level") == "high":
                recommendations.append({
                    "category": "risk_mitigation",
                    "priority": "critical",
                    "title": "Address Channel Risks",
                    "description": "High-risk factors detected that could impact channel performance.",
                    "actions": [
                        "Diversify content topics",
                        "Build stronger audience retention",
                        "Improve content quality consistency",
                        "Monitor competitor activities"
                    ]
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return []
    
    def _calculate_consistency_score(self, videos: List[Dict]) -> float:
        """Calculate content consistency score."""
        if len(videos) < 2:
            return 0.0
        
        # Calculate posting frequency consistency
        dates = [v.get("published_at") for v in videos if v.get("published_at")]
        if len(dates) < 2:
            return 0.0
        
        # Sort dates and calculate intervals
        dates.sort()
        intervals = []
        for i in range(1, len(dates)):
            try:
                date1 = datetime.fromisoformat(dates[i-1].replace('Z', '+00:00'))
                date2 = datetime.fromisoformat(dates[i].replace('Z', '+00:00'))
                intervals.append((date2 - date1).days)
            except:
                continue
        
        if not intervals:
            return 0.0
        
        # Calculate consistency (lower variance = higher consistency)
        mean_interval = np.mean(intervals)
        variance = np.var(intervals)
        consistency = max(0, 1 - (variance / (mean_interval ** 2)))
        
        return consistency
    
    def _analyze_health_trends(self, videos: List[Dict]) -> Dict[str, Any]:
        """Analyze health trends over time."""
        try:
            # Sort videos by date
            sorted_videos = sorted(videos, key=lambda x: x.get("published_at", ""))
            
            # Calculate rolling metrics
            window_size = min(5, len(sorted_videos))
            trends = {
                "views_trend": [],
                "engagement_trend": [],
                "retention_trend": []
            }
            
            for i in range(window_size, len(sorted_videos) + 1):
                window = sorted_videos[i-window_size:i]
                
                avg_views = np.mean([v.get("views", 0) for v in window])
                avg_engagement = np.mean([v.get("engagement_rate", 0) for v in window])
                avg_retention = np.mean([v.get("retention_rate", 0) for v in window])
                
                trends["views_trend"].append(avg_views)
                trends["engagement_trend"].append(avg_engagement)
                trends["retention_trend"].append(avg_retention)
            
            # Calculate trend direction
            trend_directions = {}
            for metric, values in trends.items():
                if len(values) >= 2:
                    slope = (values[-1] - values[0]) / len(values)
                    if slope > 0.05:
                        trend_directions[metric] = "increasing"
                    elif slope < -0.05:
                        trend_directions[metric] = "decreasing"
                    else:
                        trend_directions[metric] = "stable"
                else:
                    trend_directions[metric] = "unknown"
            
            return {
                "trends": trends,
                "trend_directions": trend_directions
            }
            
        except Exception as e:
            logger.error(f"Error analyzing health trends: {str(e)}")
            return {"trends": {}, "trend_directions": {}}
    
    def _cluster_content_performance(self, videos: List[Dict]) -> Dict[str, Any]:
        """Cluster content by performance characteristics."""
        try:
            if len(videos) < 5:
                return {"status": "insufficient_data"}
            
            # Extract features for clustering
            features = []
            video_info = []
            
            for video in videos:
                feature_vector = [
                    video.get("views", 0),
                    video.get("engagement_rate", 0),
                    video.get("retention_rate", 0),
                    video.get("duration", 0),
                    len(video.get("title", "")),
                    len(video.get("description", ""))
                ]
                features.append(feature_vector)
                video_info.append({
                    "title": video.get("title", ""),
                    "views": video.get("views", 0)
                })
            
            # Normalize features
            features_scaled = self.scaler.fit_transform(features)
            
            # Perform clustering
            n_clusters = min(5, len(videos) // 2)
            if n_clusters < 2:
                n_clusters = 2
            
            self.clustering_model.n_clusters = n_clusters
            cluster_labels = self.clustering_model.fit_predict(features_scaled)
            
            # Analyze clusters
            clusters = defaultdict(list)
            for i, label in enumerate(cluster_labels):
                clusters[label].append({
                    **video_info[i],
                    "features": features[i]
                })
            
            # Calculate cluster characteristics
            cluster_analysis = {}
            for cluster_id, cluster_videos in clusters.items():
                avg_views = np.mean([v["features"][0] for v in cluster_videos])
                avg_engagement = np.mean([v["features"][1] for v in cluster_videos])
                
                cluster_analysis[f"cluster_{cluster_id}"] = {
                    "video_count": len(cluster_videos),
                    "avg_views": avg_views,
                    "avg_engagement": avg_engagement,
                    "performance_level": self._classify_performance_level(avg_views, avg_engagement),
                    "sample_videos": cluster_videos[:3]
                }
            
            return {
                "clusters": cluster_analysis,
                "total_clusters": len(clusters)
            }
            
        except Exception as e:
            logger.error(f"Error clustering content performance: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _classify_performance_level(self, views: float, engagement: float) -> str:
        """Classify performance level based on views and engagement."""
        if views > 100000 and engagement > 0.05:
            return "high_performance"
        elif views > 10000 and engagement > 0.03:
            return "medium_performance"
        else:
            return "low_performance"
    
    def _analyze_content_types(self, videos: List[Dict]) -> Dict[str, Any]:
        """Analyze performance by content type."""
        try:
            content_types = defaultdict(list)
            
            # Group videos by category/type
            for video in videos:
                category = video.get("category", "unknown")
                content_types[category].append(video)
            
            # Analyze each content type
            type_analysis = {}
            for content_type, type_videos in content_types.items():
                avg_views = np.mean([v.get("views", 0) for v in type_videos])
                avg_engagement = np.mean([v.get("engagement_rate", 0) for v in type_videos])
                total_videos = len(type_videos)
                
                type_analysis[content_type] = {
                    "video_count": total_videos,
                    "avg_views": round(avg_views, 2),
                    "avg_engagement": round(avg_engagement, 4),
                    "total_views": sum(v.get("views", 0) for v in type_videos),
                    "performance_score": self._calculate_type_performance_score(avg_views, avg_engagement)
                }
            
            # Rank content types by performance
            ranked_types = sorted(
                type_analysis.items(),
                key=lambda x: x[1]["performance_score"],
                reverse=True
            )
            
            return {
                "content_types": type_analysis,
                "ranked_performance": ranked_types,
                "best_performing_type": ranked_types[0][0] if ranked_types else None
            }
            
        except Exception as e:
            logger.error(f"Error analyzing content types: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _calculate_type_performance_score(self, avg_views: float, avg_engagement: float) -> float:
        """Calculate performance score for content type."""
        # Weighted score combining views and engagement
        views_score = min(avg_views / 10000, 10)  # Cap at 10
        engagement_score = avg_engagement * 100
        
        return (views_score * 0.7) + (engagement_score * 0.3)
    
    def _analyze_posting_patterns(self, videos: List[Dict]) -> Dict[str, Any]:
        """Analyze optimal posting patterns."""
        try:
            posting_data = defaultdict(list)
            
            for video in videos:
                published_at = video.get("published_at")
                if not published_at:
                    continue
                
                try:
                    pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    day_of_week = pub_date.strftime("%A")
                    hour_of_day = pub_date.hour
                    
                    posting_data[day_of_week].append({
                        "views": video.get("views", 0),
                        "engagement": video.get("engagement_rate", 0),
                        "hour": hour_of_day
                    })
                except:
                    continue
            
            # Analyze by day of week
            day_analysis = {}
            for day, day_videos in posting_data.items():
                avg_views = np.mean([v["views"] for v in day_videos])
                avg_engagement = np.mean([v["engagement"] for v in day_videos])
                
                day_analysis[day] = {
                    "video_count": len(day_videos),
                    "avg_views": round(avg_views, 2),
                    "avg_engagement": round(avg_engagement, 4),
                    "performance_score": self._calculate_type_performance_score(avg_views, avg_engagement)
                }
            
            # Find best posting times
            all_hours = []
            for day_videos in posting_data.values():
                for video in day_videos:
                    all_hours.append({
                        "hour": video["hour"],
                        "views": video["views"],
                        "engagement": video["engagement"]
                    })
            
            hour_analysis = defaultdict(list)
            for video in all_hours:
                hour_analysis[video["hour"]].append(video)
            
            best_hours = {}
            for hour, hour_videos in hour_analysis.items():
                if len(hour_videos) >= 2:  # Need at least 2 videos for meaningful analysis
                    avg_views = np.mean([v["views"] for v in hour_videos])
                    avg_engagement = np.mean([v["engagement"] for v in hour_videos])
                    
                    best_hours[hour] = {
                        "avg_views": round(avg_views, 2),
                        "avg_engagement": round(avg_engagement, 4),
                        "video_count": len(hour_videos)
                    }
            
            # Find optimal posting schedule
            best_day = max(day_analysis.items(), key=lambda x: x[1]["performance_score"])[0] if day_analysis else None
            best_hour = max(best_hours.items(), key=lambda x: x[1]["avg_views"])[0] if best_hours else None
            
            return {
                "day_analysis": day_analysis,
                "hour_analysis": best_hours,
                "optimal_schedule": {
                    "best_day": best_day,
                    "best_hour": best_hour
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing posting patterns: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _analyze_content_lifecycle(self, videos: List[Dict]) -> Dict[str, Any]:
        """Analyze content lifecycle and longevity."""
        try:
            lifecycle_data = []
            
            for video in videos:
                published_at = video.get("published_at")
                if not published_at:
                    continue
                
                try:
                    pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    days_since_publish = (datetime.now(pub_date.tzinfo) - pub_date).days
                    
                    lifecycle_data.append({
                        "days_old": days_since_publish,
                        "views": video.get("views", 0),
                        "engagement_rate": video.get("engagement_rate", 0),
                        "title": video.get("title", "")
                    })
                except:
                    continue
            
            if not lifecycle_data:
                return {"status": "insufficient_data"}
            
            # Analyze performance by age groups
            age_groups = {
                "new": [v for v in lifecycle_data if v["days_old"] <= 7],
                "recent": [v for v in lifecycle_data if 7 < v["days_old"] <= 30],
                "mature": [v for v in lifecycle_data if 30 < v["days_old"] <= 90],
                "old": [v for v in lifecycle_data if v["days_old"] > 90]
            }
            
            lifecycle_analysis = {}
            for age_group, videos in age_groups.items():
                if videos:
                    avg_views = np.mean([v["views"] for v in videos])
                    avg_engagement = np.mean([v["engagement_rate"] for v in videos])
                    
                    lifecycle_analysis[age_group] = {
                        "video_count": len(videos),
                        "avg_views": round(avg_views, 2),
                        "avg_engagement": round(avg_engagement, 4),
                        "view_decay_rate": self._calculate_decay_rate(videos)
                    }
            
            # Identify evergreen content
            evergreen_threshold = 0.8  # 80% of peak performance maintained
            evergreen_content = []
            
            for video in lifecycle_data:
                if video["days_old"] > 30:  # Must be at least 30 days old
                    recent_performance = video["views"] / max(1, video["days_old"])
                    if recent_performance > evergreen_threshold:
                        evergreen_content.append({
                            "title": video["title"],
                            "days_old": video["days_old"],
                            "views": video["views"],
                            "performance_ratio": recent_performance
                        })
            
            return {
                "lifecycle_analysis": lifecycle_analysis,
                "evergreen_content": evergreen_content[:10],  # Top 10
                "content_longevity_score": self._calculate_longevity_score(lifecycle_data)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing content lifecycle: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _calculate_decay_rate(self, videos: List[Dict]) -> float:
        """Calculate view decay rate for a group of videos."""
        if len(videos) < 2:
            return 0.0
        
        # Sort by age
        sorted_videos = sorted(videos, key=lambda x: x["days_old"])
        
        # Calculate decay using linear regression approximation
        ages = [v["days_old"] for v in sorted_videos]
        views = [v["views"] for v in sorted_videos]
        
        if len(ages) < 2:
            return 0.0
        
        # Simple linear decay calculation
        correlation = np.corrcoef(ages, views)[0, 1] if len(ages) > 1 else 0
        decay_rate = max(0, -correlation)  # Negative correlation indicates decay
        
        return round(decay_rate, 4)
    
    def _calculate_longevity_score(self, lifecycle_data: List[Dict]) -> float:
        """Calculate overall content longevity score."""
        if not lifecycle_data:
            return 0.0
        
        # Score based on how well content maintains performance over time
        total_score = 0
        for video in lifecycle_data:
            age_factor = min(1.0, video["days_old"] / 365)  # Normalize by year
            performance_factor = video["views"] / max(1, video["days_old"])
            total_score += age_factor * performance_factor
        
        return round(total_score / len(lifecycle_data), 4)
    
    def _analyze_engagement_patterns(self, videos: List[Dict]) -> Dict[str, Any]:
        """Analyze audience engagement patterns."""
        try:
            engagement_data = []
            
            for video in videos:
                engagement_rate = video.get("engagement_rate", 0)
                views = video.get("views", 0)
                likes = video.get("likes", 0)
                comments = video.get("comments", 0)
                shares = video.get("shares", 0)
                
                engagement_data.append({
                    "engagement_rate": engagement_rate,
                    "views": views,
                    "likes": likes,
                    "comments": comments,
                    "shares": shares,
                    "like_ratio": likes / max(1, views),
                    "comment_ratio": comments / max(1, views),
                    "share_ratio": shares / max(1, views)
                })
            
            if not engagement_data:
                return {"status": "insufficient_data"}
            
            # Calculate average engagement metrics
            avg_engagement = np.mean([d["engagement_rate"] for d in engagement_data])
            avg_like_ratio = np.mean([d["like_ratio"] for d in engagement_data])
            avg_comment_ratio = np.mean([d["comment_ratio"] for d in engagement_data])
            avg_share_ratio = np.mean([d["share_ratio"] for d in engagement_data])
            
            # Identify engagement patterns
            high_engagement_videos = [d for d in engagement_data if d["engagement_rate"] > avg_engagement * 1.5]
            low_engagement_videos = [d for d in engagement_data if d["engagement_rate"] < avg_engagement * 0.5]
            
            # Engagement trend analysis
            engagement_trend = self._analyze_engagement_trend(engagement_data)
            
            return {
                "average_engagement": round(avg_engagement, 4),
                "engagement_breakdown": {
                    "like_ratio": round(avg_like_ratio, 6),
                    "comment_ratio": round(avg_comment_ratio, 6),
                    "share_ratio": round(avg_share_ratio, 6)
                },
                "high_engagement_count": len(high_engagement_videos),
                "low_engagement_count": len(low_engagement_videos),
                "engagement_consistency": self._calculate_engagement_consistency(engagement_data),
                "engagement_trend": engagement_trend
            }
            
        except Exception as e:
            logger.error(f"Error analyzing engagement patterns: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _analyze_engagement_trend(self, engagement_data: List[Dict]) -> str:
        """Analyze engagement trend direction."""
        if len(engagement_data) < 3:
            return "insufficient_data"
        
        # Take recent vs older engagement rates
        recent_engagement = np.mean([d["engagement_rate"] for d in engagement_data[-5:]])
        older_engagement = np.mean([d["engagement_rate"] for d in engagement_data[:-5]]) if len(engagement_data) > 5 else recent_engagement
        
        if recent_engagement > older_engagement * 1.1:
            return "improving"
        elif recent_engagement < older_engagement * 0.9:
            return "declining"
        else:
            return "stable"
    
    def _calculate_engagement_consistency(self, engagement_data: List[Dict]) -> float:
        """Calculate engagement consistency score."""
        if len(engagement_data) < 2:
            return 0.0
        
        engagement_rates = [d["engagement_rate"] for d in engagement_data]
        mean_engagement = np.mean(engagement_rates)
        std_engagement = np.std(engagement_rates)
        
        # Consistency score (lower variance = higher consistency)
        if mean_engagement == 0:
            return 0.0
        
        coefficient_of_variation = std_engagement / mean_engagement
        consistency_score = max(0, 1 - coefficient_of_variation)
        
        return round(consistency_score, 4)
    
    def _analyze_retention_patterns(self, videos: List[Dict]) -> Dict[str, Any]:
        """Analyze audience retention patterns."""
        try:
            retention_data = [v.get("retention_rate", 0) for v in videos if v.get("retention_rate")]
            
            if not retention_data:
                return {"status": "insufficient_data"}
            
            avg_retention = np.mean(retention_data)
            median_retention = np.median(retention_data)
            retention_std = np.std(retention_data)
            
            # Classify retention performance
            high_retention_count = len([r for r in retention_data if r > 0.7])
            medium_retention_count = len([r for r in retention_data if 0.4 <= r <= 0.7])
            low_retention_count = len([r for r in retention_data if r < 0.4])
            
            # Retention trend
            if len(retention_data) >= 5:
                recent_retention = np.mean(retention_data[-5:])
                older_retention = np.mean(retention_data[:-5]) if len(retention_data) > 5 else recent_retention
                
                if recent_retention > older_retention * 1.05:
                    retention_trend = "improving"
                elif recent_retention < older_retention * 0.95:
                    retention_trend = "declining"
                else:
                    retention_trend = "stable"
            else:
                retention_trend = "insufficient_data"
            
            return {
                "average_retention": round(avg_retention, 4),
                "median_retention": round(median_retention, 4),
                "retention_consistency": round(1 - (retention_std / max(avg_retention, 0.01)), 4),
                "retention_distribution": {
                    "high_retention": high_retention_count,
                    "medium_retention": medium_retention_count,
                    "low_retention": low_retention_count
                },
                "retention_trend": retention_trend
            }
            
        except Exception as e:
            logger.error(f"Error analyzing retention patterns: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _analyze_comment_sentiment(self, videos: List[Dict]) -> Dict[str, Any]:
        """Analyze comment sentiment patterns."""
        try:
            # This is a simplified sentiment analysis
            # In production, you'd use a proper NLP library
            
            total_comments = sum(v.get("comments", 0) for v in videos)
            avg_comments_per_video = total_comments / len(videos) if videos else 0
            
            # Estimate sentiment based on engagement patterns
            # Higher engagement often correlates with positive sentiment
            high_engagement_videos = [v for v in videos if v.get("engagement_rate", 0) > 0.05]
            positive_sentiment_estimate = len(high_engagement_videos) / len(videos) if videos else 0
            
            return {
                "total_comments": total_comments,
                "avg_comments_per_video": round(avg_comments_per_video, 2),
                "estimated_positive_sentiment": round(positive_sentiment_estimate, 4),
                "comment_engagement_ratio": round(total_comments / max(1, sum(v.get("views", 0) for v in videos)), 6)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing comment sentiment: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _analyze_audience_growth(self, channel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze audience growth patterns."""
        try:
            # Extract subscriber data if available
            subscriber_history = channel_data.get("subscriber_history", [])
            
            if not subscriber_history:
                # Estimate growth from video performance
                videos = channel_data.get("videos", [])
                estimated_growth = sum(v.get("new_subscribers", 0) for v in videos)
                
                return {
                    "estimated_subscriber_growth": estimated_growth,
                    "growth_rate": "estimated",
                    "status": "estimated_data"
                }
            
            # Calculate growth metrics from actual data
            if len(subscriber_history) >= 2:
                current_subs = subscriber_history[-1].get("count", 0)
                previous_subs = subscriber_history[0].get("count", 0)
                
                growth_rate = (current_subs - previous_subs) / max(1, previous_subs)
                
                return {
                    "current_subscribers": current_subs,
                    "growth_rate": round(growth_rate, 4),
                    "net_growth": current_subs - previous_subs,
                    "growth_trend": "increasing" if growth_rate > 0 else "decreasing"
                }
            
            return {"status": "insufficient_data"}
            
        except Exception as e:
            logger.error(f"Error analyzing audience growth: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _analyze_demographics(self, channel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze audience demographics if available."""
        try:
            demographics = channel_data.get("demographics", {})
            
            if not demographics:
                return {"status": "no_demographic_data"}
            
            # Analyze age distribution
            age_distribution = demographics.get("age_groups", {})
            
            # Analyze geographic distribution
            geographic_distribution = demographics.get("countries", {})
            
            # Analyze device usage
            device_distribution = demographics.get("devices", {})
            
            return {
                "age_distribution": age_distribution,
                "geographic_distribution": geographic_distribution,
                "device_distribution": device_distribution,
                "primary_audience": self._identify_primary_audience(demographics)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing demographics: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _identify_primary_audience(self, demographics: Dict[str, Any]) -> Dict[str, str]:
        """Identify primary audience characteristics."""
        try:
            primary_audience = {}
            
            # Primary age group
            age_groups = demographics.get("age_groups", {})
            if age_groups:
                primary_age = max(age_groups.items(), key=lambda x: x[1])[0]
                primary_audience["age_group"] = primary_age
            
            # Primary country
            countries = demographics.get("countries", {})
            if countries:
                primary_country = max(countries.items(), key=lambda x: x[1])[0]
                primary_audience["country"] = primary_country
            
            # Primary device
            devices = demographics.get("devices", {})
            if devices:
                primary_device = max(devices.items(), key=lambda x: x[1])[0]
                primary_audience["device"] = primary_device
            
            return primary_audience
            
        except Exception as e:
            logger.error(f"Error identifying primary audience: {str(e)}")
            return {}
    
    def _calculate_growth_metrics(self, channel_data: Dict[str, Any], time_period: int) -> Dict[str, Any]:
        """Calculate comprehensive growth metrics."""
        try:
            videos = channel_data.get("videos", [])
            if not videos:
                return {"status": "insufficient_data"}
            
            # Filter videos within time period
            cutoff_date = datetime.now() - timedelta(days=time_period)
            recent_videos = []
            
            for video in videos:
                published_at = video.get("published_at")
                if published_at:
                    try:
                        pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                        if pub_date >= cutoff_date:
                            recent_videos.append(video)
                    except:
                        continue
            
            if not recent_videos:
                return {"status": "no_recent_data"}
            
            # Calculate growth metrics
            total_views = sum(v.get("views", 0) for v in recent_videos)
            total_subscribers_gained = sum(v.get("new_subscribers", 0) for v in recent_videos)
            avg_views_per_video = total_views / len(recent_videos)
            
            # Calculate growth rates
            video_count_growth = len(recent_videos) / time_period  # Videos per day
            view_growth_rate = total_views / max(1, len(videos) - len(recent_videos))  # Compared to older videos
            
            # Engagement growth
            recent_engagement = np.mean([v.get("engagement_rate", 0) for v in recent_videos])
            older_videos = [v for v in videos if v not in recent_videos]
            older_engagement = np.mean([v.get("engagement_rate", 0) for v in older_videos]) if older_videos else recent_engagement
            
            engagement_growth_rate = (recent_engagement - older_engagement) / max(0.001, older_engagement)
            
            return {
                "time_period_days": time_period,
                "videos_published": len(recent_videos),
                "total_views": total_views,
                "avg_views_per_video": round(avg_views_per_video, 2),
                "subscribers_gained": total_subscribers_gained,
                "video_frequency": round(video_count_growth, 2),
                "view_growth_rate": round(view_growth_rate, 4),
                "engagement_growth_rate": round(engagement_growth_rate, 4),
                "growth_momentum": self._calculate_growth_momentum(recent_videos)
            }
            
        except Exception as e:
            logger.error(f"Error calculating growth metrics: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _calculate_growth_momentum(self, recent_videos: List[Dict]) -> str:
        """Calculate growth momentum based on recent performance."""
        if len(recent_videos) < 3:
            return "insufficient_data"
        
        # Sort by publication date
        sorted_videos = sorted(recent_videos, key=lambda x: x.get("published_at", ""))
        
        # Compare first half vs second half performance
        mid_point = len(sorted_videos) // 2
        first_half = sorted_videos[:mid_point]
        second_half = sorted_videos[mid_point:]
        
        first_half_avg = np.mean([v.get("views", 0) for v in first_half])
        second_half_avg = np.mean([v.get("views", 0) for v in second_half])
        
        if second_half_avg > first_half_avg * 1.2:
            return "accelerating"
        elif second_half_avg < first_half_avg * 0.8:
            return "decelerating"
        else:
            return "steady"
    
    def _analyze_growth_trends(self, channel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze long-term growth trends."""
        try:
            videos = channel_data.get("videos", [])
            if len(videos) < 10:
                return {"status": "insufficient_data"}
            
            # Sort videos by date
            sorted_videos = sorted(videos, key=lambda x: x.get("published_at", ""))
            
            # Calculate rolling averages
            window_size = min(5, len(sorted_videos) // 4)
            rolling_metrics = {
                "views": [],
                "engagement": [],
                "subscribers": []
            }
            
            for i in range(window_size, len(sorted_videos) + 1):
                window = sorted_videos[i-window_size:i]
                
                avg_views = np.mean([v.get("views", 0) for v in window])
                avg_engagement = np.mean([v.get("engagement_rate", 0) for v in window])
                avg_subscribers = np.mean([v.get("new_subscribers", 0) for v in window])
                
                rolling_metrics["views"].append(avg_views)
                rolling_metrics["engagement"].append(avg_engagement)
                rolling_metrics["subscribers"].append(avg_subscribers)
            
            # Analyze trends
            trends = {}
            for metric, values in rolling_metrics.items():
                if len(values) >= 3:
                    # Simple trend analysis using first and last values
                    trend_slope = (values[-1] - values[0]) / len(values)
                    
                    if trend_slope > 0.1:
                        trends[metric] = "strong_upward"
                    elif trend_slope > 0:
                        trends[metric] = "upward"
                    elif trend_slope < -0.1:
                        trends[metric] = "strong_downward"
                    elif trend_slope < 0:
                        trends[metric] = "downward"
                    else:
                        trends[metric] = "stable"
                else:
                    trends[metric] = "insufficient_data"
            
            # Overall trend assessment
            positive_trends = sum(1 for t in trends.values() if "upward" in t)
            negative_trends = sum(1 for t in trends.values() if "downward" in t)
            
            if positive_trends > negative_trends:
                overall_trend = "positive"
            elif negative_trends > positive_trends:
                overall_trend = "negative"
            else:
                overall_trend = "mixed"
            
            return {
                "individual_trends": trends,
                "overall_trend": overall_trend,
                "trend_strength": abs(positive_trends - negative_trends),
                "rolling_metrics": rolling_metrics
            }
            
        except Exception as e:
            logger.error(f"Error analyzing growth trends: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _analyze_growth_acceleration(self, channel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze growth acceleration/deceleration patterns."""
        try:
            videos = channel_data.get("videos", [])
            if len(videos) < 6:
                return {"status": "insufficient_data"}
            
            # Sort videos by date
            sorted_videos = sorted(videos, key=lambda x: x.get("published_at", ""))
            
            # Divide into three periods
            period_size = len(sorted_videos) // 3
            periods = {
                "early": sorted_videos[:period_size],
                "middle": sorted_videos[period_size:2*period_size],
                "recent": sorted_videos[2*period_size:]
            }
            
            # Calculate metrics for each period
            period_metrics = {}
            for period_name, period_videos in periods.items():
                avg_views = np.mean([v.get("views", 0) for v in period_videos])
                avg_engagement = np.mean([v.get("engagement_rate", 0) for v in period_videos])
                
                period_metrics[period_name] = {
                    "avg_views": avg_views,
                    "avg_engagement": avg_engagement,
                    "video_count": len(period_videos)
                }
            
            # Calculate acceleration
            view_acceleration = self._calculate_acceleration(
                period_metrics["early"]["avg_views"],
                period_metrics["middle"]["avg_views"],
                period_metrics["recent"]["avg_views"]
            )
            
            engagement_acceleration = self._calculate_acceleration(
                period_metrics["early"]["avg_engagement"],
                period_metrics["middle"]["avg_engagement"],
                period_metrics["recent"]["avg_engagement"]
            )
            
            return {
                "period_metrics": period_metrics,
                "view_acceleration": view_acceleration,
                "engagement_acceleration": engagement_acceleration,
                "overall_acceleration": self._classify_acceleration(view_acceleration, engagement_acceleration)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing growth acceleration: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _calculate_acceleration(self, early: float, middle: float, recent: float) -> float:
        """Calculate acceleration between three time periods."""
        if early == 0 or middle == 0:
            return 0.0
        
        # Calculate rate of change between periods
        first_change = (middle - early) / early
        second_change = (recent - middle) / middle
        
        # Acceleration is the change in rate of change
        acceleration = second_change - first_change
        return round(acceleration, 4)
    
    def _classify_acceleration(self, view_accel: float, engagement_accel: float) -> str:
        """Classify overall acceleration pattern."""
        avg_accel = (view_accel + engagement_accel) / 2
        
        if avg_accel > 0.1:
            return "strong_acceleration"
        elif avg_accel > 0:
            return "mild_acceleration"
        elif avg_accel < -0.1:
            return "strong_deceleration"
        elif avg_accel < 0:
            return "mild_deceleration"
        else:
            return "stable"
    
    def _analyze_seasonal_patterns(self, channel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze seasonal performance patterns."""
        try:
            videos = channel_data.get("videos", [])
            if len(videos) < 12:  # Need at least a year of data
                return {"status": "insufficient_data"}
            
            # Group videos by month
            monthly_data = defaultdict(list)
            
            for video in videos:
                published_at = video.get("published_at")
                if published_at:
                    try:
                        pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                        month = pub_date.strftime("%B")
                        monthly_data[month].append(video)
                    except:
                        continue
            
            # Calculate monthly averages
            monthly_performance = {}
            for month, month_videos in monthly_data.items():
                if month_videos:
                    avg_views = np.mean([v.get("views", 0) for v in month_videos])
                    avg_engagement = np.mean([v.get("engagement_rate", 0) for v in month_videos])
                    
                    monthly_performance[month] = {
                        "avg_views": round(avg_views, 2),
                        "avg_engagement": round(avg_engagement, 4),
                        "video_count": len(month_videos)
                    }
            
            # Identify best and worst performing months
            if monthly_performance:
                best_month = max(monthly_performance.items(), key=lambda x: x[1]["avg_views"])
                worst_month = min(monthly_performance.items(), key=lambda x: x[1]["avg_views"])
                
                return {
                    "monthly_performance": monthly_performance,
                    "best_month": {
                        "month": best_month[0],
                        "avg_views": best_month[1]["avg_views"]
                    },
                    "worst_month": {
                        "month": worst_month[0],
                        "avg_views": worst_month[1]["avg_views"]
                    },
                    "seasonality_strength": self._calculate_seasonality_strength(monthly_performance)
                }
            
            return {"status": "no_seasonal_data"}
            
        except Exception as e:
            logger.error(f"Error analyzing seasonal patterns: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _calculate_seasonality_strength(self, monthly_performance: Dict[str, Dict]) -> float:
        """Calculate the strength of seasonal patterns."""
        if len(monthly_performance) < 3:
            return 0.0
        
        view_values = [data["avg_views"] for data in monthly_performance.values()]
        mean_views = np.mean(view_values)
        std_views = np.std(view_values)
        
        # Coefficient of variation as seasonality measure
        if mean_views > 0:
            seasonality = std_views / mean_views
            return round(min(1.0, seasonality), 4)
        
        return 0.0
    
    def _forecast_growth(self, channel_data: Dict[str, Any], time_period: int) -> Dict[str, Any]:
        """Forecast future growth based on historical data."""
        try:
            videos = channel_data.get("videos", [])
            if len(videos) < 5:
                return {"status": "insufficient_data"}
            
            # Extract time series data
            time_series_data = []
            for video in videos:
                published_at = video.get("published_at")
                if published_at:
                    try:
                        pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                        days_ago = (datetime.now(pub_date.tzinfo) - pub_date).days
                        
                        time_series_data.append({
                            "days_ago": days_ago,
                            "views": video.get("views", 0),
                            "engagement": video.get("engagement_rate", 0)
                        })
                    except:
                        continue
            
            if len(time_series_data) < 3:
                return {"status": "insufficient_time_series_data"}
            
            # Sort by days ago (most recent first)
            time_series_data.sort(key=lambda x: x["days_ago"])
            
            # Simple linear trend forecasting
            recent_data = time_series_data[:min(10, len(time_series_data))]
            
            # Calculate trend
            days = [d["days_ago"] for d in recent_data]
            views = [d["views"] for d in recent_data]
            
            if len(days) >= 2:
                # Simple linear regression
                view_trend = (views[-1] - views[0]) / (days[-1] - days[0]) if days[-1] != days[0] else 0
                
                # Forecast next period
                forecast_days = min(30, time_period)  # Forecast up to 30 days
                forecasted_views = views[-1] + (view_trend * forecast_days)
                
                # Calculate confidence based on trend consistency
                view_variance = np.var(views)
                confidence = max(0.1, min(0.9, 1 - (view_variance / max(1, np.mean(views)))))
                
                return {
                    "forecast_period_days": forecast_days,
                    "forecasted_avg_views": max(0, round(forecasted_views, 2)),
                    "trend_direction": "increasing" if view_trend > 0 else "decreasing",
                    "trend_strength": abs(view_trend),
                    "confidence_level": round(confidence, 2),
                    "forecast_range": {
                        "low": max(0, round(forecasted_views * (1 - (1 - confidence)), 2)),
                        "high": round(forecasted_views * (1 + (1 - confidence)), 2)
                    }
                }
            
            return {"status": "insufficient_trend_data"}
            
        except Exception as e:
            logger.error(f"Error forecasting growth: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _analyze_revenue_per_view(self, videos: List[Dict]) -> Dict[str, Any]:
        """Analyze revenue per view metrics."""
        try:
            revenue_data = []
            
            for video in videos:
                views = video.get("views", 0)
                ad_revenue = video.get("ad_revenue", 0)
                sponsorship_revenue = video.get("sponsorship_revenue", 0)
                affiliate_revenue = video.get("affiliate_revenue", 0)
                
                total_revenue = ad_revenue + sponsorship_revenue + affiliate_revenue
                rpv = total_revenue / max(1, views)
                
                revenue_data.append({
                    "views": views,
                    "total_revenue": total_revenue,
                    "rpv": rpv,
                    "ad_revenue": ad_revenue,
                    "sponsorship_revenue": sponsorship_revenue,
                    "affiliate_revenue": affiliate_revenue
                })
            
            if not revenue_data:
                return {"status": "no_revenue_data"}
            
            # Calculate averages
            avg_rpv = np.mean([d["rpv"] for d in revenue_data])
            median_rpv = np.median([d["rpv"] for d in revenue_data])
            total_revenue = sum(d["total_revenue"] for d in revenue_data)
            total_views = sum(d["views"] for d in revenue_data)
            
            # Identify high-performing videos
            high_rpv_videos = [d for d in revenue_data if d["rpv"] > avg_rpv * 1.5]
            
            return {
                "average_rpv": round(avg_rpv, 6),
                "median_rpv": round(median_rpv, 6),
                "total_revenue": round(total_revenue, 2),
                "total_views": total_views,
                "overall_rpv": round(total_revenue / max(1, total_views), 6),
                "high_rpv_video_count": len(high_rpv_videos),
                "revenue_consistency": self._calculate_revenue_consistency(revenue_data)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing revenue per view: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _calculate_revenue_consistency(self, revenue_data: List[Dict]) -> float:
        """Calculate revenue consistency score."""
        if len(revenue_data) < 2:
            return 0.0
        
        rpv_values = [d["rpv"] for d in revenue_data]
        mean_rpv = np.mean(rpv_values)
        std_rpv = np.std(rpv_values)
        
        if mean_rpv == 0:
            return 0.0
        
        coefficient_of_variation = std_rpv / mean_rpv
        consistency = max(0, 1 - coefficient_of_variation)
        
        return round(consistency, 4)
    
    def _analyze_monetization_channels(self, videos: List[Dict]) -> Dict[str, Any]:
        """Analyze different monetization channels."""
        try:
            channel_totals = {
                "ad_revenue": 0,
                "sponsorship_revenue": 0,
                "affiliate_revenue": 0
            }
            
            for video in videos:
                channel_totals["ad_revenue"] += video.get("ad_revenue", 0)
                channel_totals["sponsorship_revenue"] += video.get("sponsorship_revenue", 0)
                channel_totals["affiliate_revenue"] += video.get("affiliate_revenue", 0)
            
            total_revenue = sum(channel_totals.values())
            
            if total_revenue == 0:
                return {"status": "no_revenue_data"}
            
            # Calculate percentages
            channel_percentages = {
                channel: round((revenue / total_revenue) * 100, 2)
                for channel, revenue in channel_totals.items()
            }
            
            # Identify primary revenue source
            primary_channel = max(channel_totals.items(), key=lambda x: x[1])
            
            # Calculate diversification score
            diversification_score = self._calculate_diversification_score(channel_percentages)
            
            return {
                "revenue_by_channel": channel_totals,
                "percentage_by_channel": channel_percentages,
                "primary_revenue_source": {
                    "channel": primary_channel[0],
                    "amount": primary_channel[1],
                    "percentage": channel_percentages[primary_channel[0]]
                },
                "diversification_score": diversification_score,
                "total_revenue": total_revenue
            }
            
        except Exception as e:
            logger.error(f"Error analyzing monetization channels: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _calculate_diversification_score(self, channel_percentages: Dict[str, float]) -> float:
        """Calculate revenue diversification score."""
        # Higher score means more diversified revenue
        percentages = list(channel_percentages.values())
        
        # Calculate entropy-based diversification
        entropy = 0
        for percentage in percentages:
            if percentage > 0:
                p = percentage / 100
                entropy -= p * np.log2(p)
        
        # Normalize to 0-1 scale
        max_entropy = np.log2(len(percentages))
        diversification = entropy / max_entropy if max_entropy > 0 else 0
        
        return round(diversification, 4)
    
    def _identify_revenue_opportunities(self, videos: List[Dict]) -> List[Dict[str, Any]]:
        """Identify revenue optimization opportunities."""
        try:
            opportunities = []
            
            # Analyze undermonetized high-view videos
            high_view_videos = [v for v in videos if v.get("views", 0) > 10000]
            
            for video in high_view_videos:
                total_revenue = (video.get("ad_revenue", 0) + 
                               video.get("sponsorship_revenue", 0) + 
                               video.get("affiliate_revenue", 0))
                
                expected_revenue = video.get("views", 0) * 0.001  # $1 per 1000 views baseline
                
                if total_revenue < expected_revenue * 0.5:  # Less than 50% of expected
                    opportunities.append({
                        "type": "undermonetized_content",
                        "video_title": video.get("title", ""),
                        "views": video.get("views", 0),
                        "current_revenue": total_revenue,
                        "potential_revenue": expected_revenue,
                        "opportunity_value": expected_revenue - total_revenue
                    })
            
            # Identify sponsorship opportunities
            high_engagement_videos = [v for v in videos if v.get("engagement_rate", 0) > 0.05]
            unsponsored_videos = [v for v in high_engagement_videos if v.get("sponsorship_revenue", 0) == 0]
            
            if unsponsored_videos:
                avg_views = np.mean([v.get("views", 0) for v in unsponsored_videos])
                opportunities.append({
                    "type": "sponsorship_opportunity",
                    "video_count": len(unsponsored_videos),
                    "avg_views": avg_views,
                    "potential_revenue": avg_views * 0.002 * len(unsponsored_videos)  # $2 per 1000 views
                })
            
            # Sort by opportunity value
            opportunities.sort(key=lambda x: x.get("opportunity_value", x.get("potential_revenue", 0)), reverse=True)
            
            return opportunities[:10]  # Top 10 opportunities
            
        except Exception as e:
            logger.error(f"Error identifying revenue opportunities: {str(e)}")
            return []
    
    def _analyze_cpm_trends(self, videos: List[Dict]) -> Dict[str, Any]:
        """Analyze CPM (Cost Per Mille) trends."""
        try:
            cpm_data = []
            
            for video in videos:
                views = video.get("views", 0)
                ad_revenue = video.get("ad_revenue", 0)
                
                if views > 0:
                    cpm = (ad_revenue / views) * 1000  # CPM calculation
                    published_at = video.get("published_at")
                    
                    if published_at:
                        try:
                            pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                            cpm_data.append({
                                "cpm": cpm,
                                "date": pub_date,
                                "views": views,
                                "revenue": ad_revenue
                            })
                        except:
                            continue
            
            if not cpm_data:
                return {"status": "no_cpm_data"}
            
            # Sort by date
            cpm_data.sort(key=lambda x: x["date"])
            
            # Calculate averages
            avg_cpm = np.mean([d["cpm"] for d in cpm_data])
            median_cpm = np.median([d["cpm"] for d in cpm_data])
            
            # Analyze trend
            if len(cpm_data) >= 5:
                recent_cpm = np.mean([d["cpm"] for d in cpm_data[-5:]])
                older_cpm = np.mean([d["cpm"] for d in cpm_data[:-5]])
                
                cpm_trend = "increasing" if recent_cpm > older_cpm * 1.05 else "decreasing" if recent_cpm < older_cpm * 0.95 else "stable"
            else:
                cpm_trend = "insufficient_data"
            
            return {
                "average_cpm": round(avg_cpm, 4),
                "median_cpm": round(median_cpm, 4),
                "cpm_trend": cpm_trend,
                "cpm_range": {
                    "min": round(min(d["cpm"] for d in cpm_data), 4),
                    "max": round(max(d["cpm"] for d in cpm_data), 4)
                },
                "data_points": len(cpm_data)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing CPM trends: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _forecast_revenue(self, videos: List[Dict]) -> Dict[str, Any]:
        """Forecast future revenue based on historical data."""
        try:
            # Extract revenue time series
            revenue_data = []
            
            for video in videos:
                published_at = video.get("published_at")
                if published_at:
                    try:
                        pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                        total_revenue = (video.get("ad_revenue", 0) + 
                                       video.get("sponsorship_revenue", 0) + 
                                       video.get("affiliate_revenue", 0))
                        
                        revenue_data.append({
                            "date": pub_date,
                            "revenue": total_revenue,
                            "views": video.get("views", 0)
                        })
                    except:
                        continue
            
            if len(revenue_data) < 3:
                return {"status": "insufficient_data"}
            
            # Sort by date
            revenue_data.sort(key=lambda x: x["date"])
            
            # Calculate monthly revenue
            monthly_revenue = defaultdict(float)
            for data in revenue_data:
                month_key = data["date"].strftime("%Y-%m")
                monthly_revenue[month_key] += data["revenue"]
            
            if len(monthly_revenue) < 2:
                return {"status": "insufficient_monthly_data"}
            
            # Simple trend-based forecasting
            revenue_values = list(monthly_revenue.values())
            recent_avg = np.mean(revenue_values[-3:]) if len(revenue_values) >= 3 else revenue_values[-1]
            
            # Calculate growth rate
            if len(revenue_values) >= 2:
                growth_rate = (revenue_values[-1] - revenue_values[0]) / len(revenue_values)
            else:
                growth_rate = 0
            
            # Forecast next 3 months
            forecasts = []
            for i in range(1, 4):
                forecasted_revenue = recent_avg + (growth_rate * i)
                forecasts.append({
                    "month": i,
                    "forecasted_revenue": max(0, round(forecasted_revenue, 2))
                })
            
            return {
                "historical_monthly_revenue": dict(monthly_revenue),
                "recent_monthly_average": round(recent_avg, 2),
                "growth_rate": round(growth_rate, 2),
                "forecasts": forecasts,
                "total_forecasted_revenue": sum(f["forecasted_revenue"] for f in forecasts)
            }
            
        except Exception as e:
            logger.error(f"Error forecasting revenue: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _estimate_market_position(self, channel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate market position based on channel metrics."""
        try:
            videos = channel_data.get("videos", [])
            if not videos:
                return {"status": "insufficient_data"}
            
            # Calculate key metrics
            total_views = sum(v.get("views", 0) for v in videos)
            avg_views = total_views / len(videos)
            avg_engagement = np.mean([v.get("engagement_rate", 0) for v in videos])
            
            # Estimate market position based on benchmarks
            # These would typically come from industry data
            benchmarks = {
                "micro": {"views": 1000, "engagement": 0.03},
                "small": {"views": 10000, "engagement": 0.04},
                "medium": {"views": 100000, "engagement": 0.05},
                "large": {"views": 1000000, "engagement": 0.06}
            }
            
            position = "micro"
            for tier, benchmark in benchmarks.items():
                if avg_views >= benchmark["views"] and avg_engagement >= benchmark["engagement"]:
                    position = tier
            
            return {
                "estimated_tier": position,
                "avg_views": round(avg_views, 2),
                "avg_engagement": round(avg_engagement, 4),
                "total_views": total_views,
                "video_count": len(videos),
                "benchmarks": benchmarks,
                "growth_potential": self._calculate_growth_potential(position, avg_views, avg_engagement)
            }
            
        except Exception as e:
            logger.error(f"Error estimating market position: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _calculate_growth_potential(self, current_tier: str, avg_views: float, avg_engagement: float) -> Dict[str, Any]:
        """Calculate growth potential to next tier."""
        tier_order = ["micro", "small", "medium", "large"]
        
        if current_tier not in tier_order:
            return {"status": "unknown_tier"}
        
        current_index = tier_order.index(current_tier)
        
        if current_index >= len(tier_order) - 1:
            return {
                "next_tier": "top_tier",
                "growth_needed": "continue_optimization",
                "potential": "maintain_leadership"
            }
        
        next_tier = tier_order[current_index + 1]
        benchmarks = {
            "micro": {"views": 1000, "engagement": 0.03},
            "small": {"views": 10000, "engagement": 0.04},
            "medium": {"views": 100000, "engagement": 0.05},
            "large": {"views": 1000000, "engagement": 0.06}
        }
        
        next_benchmark = benchmarks[next_tier]
        
        views_gap = max(0, next_benchmark["views"] - avg_views)
        engagement_gap = max(0, next_benchmark["engagement"] - avg_engagement)
        
        return {
            "next_tier": next_tier,
            "views_gap": round(views_gap, 2),
            "engagement_gap": round(engagement_gap, 4),
            "views_growth_needed": f"{((views_gap / max(avg_views, 1)) * 100):.1f}%",
            "engagement_improvement_needed": f"{((engagement_gap / max(avg_engagement, 0.001)) * 100):.1f}%"
        }


# Advanced Analytics API Endpoints
async def get_advanced_analytics_endpoint(
    channel_data: Dict[str, Any],
    analysis_type: str = "comprehensive",
    time_period: int = 90
):
    """
    Get advanced analytics for channel data.
    
    Args:
        channel_data (Dict[str, Any]): Channel data including videos
        analysis_type (str): Type of analysis to perform
        time_period (int): Time period in days for analysis
        
    Returns:
        APIResponse: Advanced analytics results
    """
    try:
        analytics_engine = AdvancedAnalyticsEngine()
        
        if analysis_type == "comprehensive":
            result = await analytics_engine.comprehensive_channel_analysis(channel_data, time_period)
        elif analysis_type == "predictive":
            # Assuming AdvancedAnalyticsEngine has or will have a predictive_analysis method
            # For now, let's point to a relevant existing method or placeholder
            result = await analytics_engine._generate_predictive_insights(channel_data)
        elif analysis_type == "monetization":
            result = await analytics_engine._analyze_monetization_efficiency(channel_data)
        elif analysis_type == "audience":
            result = await analytics_engine._analyze_audience_behavior(channel_data)
        else:
            raise HTTPException(status_code=400, detail="Invalid analysis type")
        
        return APIResponse(
            status="success",
            data=result,
            message="Advanced analytics completed successfully"
        )
        
    except Exception as e:
        logger.error(f"Error in advanced analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error performing advanced analytics: {str(e)}"
        )


async def get_performance_insights_endpoint(channel_data: Dict[str, Any]):
    """
    Get performance insights and recommendations.
    
    Args:
        channel_data (Dict[str, Any]): Channel data
        
    Returns:
        APIResponse: Performance insights
    """
    try:
        analytics_engine = AdvancedAnalyticsEngine()
        insights = await analytics_engine._generate_predictive_insights(channel_data) # Example, assuming this provides performance insights
        
        return APIResponse(
            status="success",
            data=insights,
            message="Performance insights generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error generating performance insights: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating performance insights: {str(e)}"
        )


async def get_growth_forecast_endpoint(
    channel_data: Dict[str, Any],
    forecast_period: int = 30
):
    """
    Get growth forecast for specified period.
    
    Args:
        channel_data (Dict[str, Any]): Channel data
        forecast_period (int): Forecast period in days
        
    Returns:
        APIResponse: Growth forecast
    """
    try:
        analytics_engine = AdvancedAnalyticsEngine()
        forecast = await analytics_engine._forecast_growth(channel_data, forecast_period)
        
        return APIResponse(
            status="success",
            data=forecast,
            message="Growth forecast generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error generating growth forecast: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating growth forecast: {str(e)}"
        )


async def get_revenue_analysis_endpoint(videos: List[Dict[str, Any]]):
    """
    Get detailed revenue analysis.
    
    Args:
        videos (List[Dict[str, Any]]): List of video data
        
    Returns:
        APIResponse: Revenue analysis
    """
    try:
        analytics_engine = AdvancedAnalyticsEngine()
        revenue_analysis = await analytics_engine._analyze_monetization_efficiency({"videos": videos})
        
        return APIResponse(
            status="success",
            data=revenue_analysis,
            message="Revenue analysis completed successfully"
        )
        
    except Exception as e:
        logger.error(f"Error in revenue analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error performing revenue analysis: {str(e)}"
        )


async def get_content_optimization_suggestions_endpoint(channel_data: Dict[str, Any]):
    """
    Get content optimization suggestions based on analytics.
    
    Args:
        channel_data (Dict[str, Any]): Channel data
        
    Returns:
        APIResponse: Optimization suggestions
    """
    try:
        analytics_engine = AdvancedAnalyticsEngine()
        
        # Perform comprehensive analysis
        analysis_results = await analytics_engine.comprehensive_channel_analysis(channel_data, 90)
        
        # Generate recommendations
        recommendations = await analytics_engine._generate_comprehensive_recommendations(analysis_results)
        
        # Add specific optimization suggestions
        optimization_suggestions = {
            "content_recommendations": recommendations,
            "posting_optimization": analysis_results.get("posting_patterns", {}),
            "engagement_optimization": analysis_results.get("engagement_analysis", {}),
            "monetization_optimization": analysis_results.get("monetization_analysis", {})
        }
        
        return APIResponse(
            status="success",
            data=optimization_suggestions,
            message="Content optimization suggestions generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error generating optimization suggestions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating optimization suggestions: {str(e)}"
        )


# Export the analytics class and endpoints
__all__ = [
    'AdvancedAnalyticsEngine',
    'get_advanced_analytics_endpoint',
    'get_performance_insights_endpoint',
    'get_growth_forecast_endpoint',
    'get_revenue_analysis_endpoint',
    'get_content_optimization_suggestions_endpoint'
]
