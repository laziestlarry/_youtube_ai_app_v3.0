from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from .advanced_analytics_utils import *
from ..database import get_all_ideas, get_db_connection
from ..utils import APIResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/api/v1/analytics/comprehensive")
async def get_comprehensive_analytics(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    include_predictions: bool = Query(True, description="Include predictive analytics")
):
    """
    Get comprehensive analytics with advanced insights.
    
    Args:
        start_date: Filter videos from this date
        end_date: Filter videos until this date
        category: Filter by specific category
        include_predictions: Whether to include predictive analytics
        
    Returns:
        APIResponse: Comprehensive analytics data
    """
    try:
        # Get video data from database
        videos = get_all_ideas()
        
        # Convert database format to analytics format
        analytics_videos = []
        for video in videos:
            analytics_video = {
                "id": video.get("id"),
                "title": video.get("title", ""),
                "category": video.get("category", "unknown"),
                "views": video.get("expected_views", 0),  # Using expected_views as proxy
                "duration": 600,  # Default 10 minutes
                "published_at": video.get("created_at", ""),
                "engagement_score": 0.035,  # Default engagement rate
                "performance_score": min(video.get("expected_views", 0) / 100, 100),
                "revenue_total": video.get("expected_views", 0) * 0.01,  # $0.01 per view
                "ad_revenue": video.get("expected_views", 0) * 0.004,
                "sponsorship_revenue": video.get("expected_views", 0) * 0.004,
                "affiliate_revenue": video.get("expected_views", 0) * 0.002
            }
            analytics_videos.append(analytics_video)
        
        # Apply filters
        if start_date:
            analytics_videos = [v for v in analytics_videos if v.get("published_at", "") >= start_date]
        if end_date:
            analytics_videos = [v for v in analytics_videos if v.get("published_at", "") <= end_date]
        if category:
            analytics_videos = [v for v in analytics_videos if v.get("category", "").lower() == category.lower()]
        
        # Generate comprehensive analytics
        analytics_data = {
            "overview": generate_analytics_overview(analytics_videos),
            "performance_analysis": analyze_performance_metrics(analytics_videos),
            "engagement_analysis": analyze_engagement_patterns(analytics_videos),
            "revenue_analysis": analyze_revenue_streams(analytics_videos),
            "content_analysis": analyze_content_patterns(analytics_videos),
            "growth_metrics": calculate_growth_metrics(analytics_videos),
            "competitive_analysis": generate_competitive_analysis(analytics_videos, category or "general"),
            "roi_analysis": calculate_content_roi(analytics_videos)
        }
        
        # Add predictive analytics if requested
        if include_predictions:
            analytics_data["predictions"] = {
                "performance_trends": predict_trends(analytics_videos),
                "revenue_forecast": forecast_revenue(analytics_videos),
                "growth_projections": calculate_audience_growth_metrics(analytics_videos, {"subscriber_count": 1000}),
                "performance_changes": predict_performance_changes(analytics_videos)
            }
        
        # Add advanced insights
        analytics_data["insights"] = generate_advanced_insights(analytics_videos, {"subscriber_count": 1000})
        
        # Add recommendations
        analytics_data["recommendations"] = {
            "priority_actions": identify_priority_actions(analytics_videos, {"subscriber_count": 1000}),
            "content_recommendations": generate_content_recommendations(analytics_videos),
            "monetization_opportunities": identify_monetization_opportunities(analytics_videos),
            "seo_recommendations": generate_seo_recommendations(analytics_videos)
        }
        
        return APIResponse(
            status="success",
            data=analytics_data,
            message="Comprehensive analytics generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error generating comprehensive analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating analytics: {str(e)}"
        )

@router.get("/api/v1/analytics/performance-dashboard")
async def get_performance_dashboard():
    """
    Get performance dashboard data with key metrics.
    
    Returns:
        APIResponse: Performance dashboard data
    """
    try:
        videos = get_all_ideas()
        
        # Convert to analytics format
        analytics_videos = []
        for video in videos:
            analytics_video = {
                "title": video.get("title", ""),
                "category": video.get("category", "unknown"),
                "views": video.get("expected_views", 0),
                "performance_score": min(video.get("expected_views", 0) / 100, 100),
                "engagement_score": 0.035,
                "revenue_total": video.get("expected_views", 0) * 0.01,
                "published_at": video.get("created_at", "")
            }
            analytics_videos.append(analytics_video)
        
        # Generate dashboard data
        dashboard_data = {
            "key_metrics": {
                "total_videos": len(analytics_videos),
                "total_views": sum(v["views"] for v in analytics_videos),
                "total_revenue": sum(v["revenue_total"] for v in analytics_videos),
                "avg_performance": mean([v["performance_score"] for v in analytics_videos]) if analytics_videos else 0,
                "avg_engagement": mean([v["engagement_score"] for v in analytics_videos]) if analytics_videos else 0
            },
            "performance_timeline": create_performance_timeline(analytics_videos),
            "top_performers": sorted(analytics_videos, key=lambda x: x["performance_score"], reverse=True)[:5],
            "category_breakdown": analyze_category_performance(analytics_videos),
            "recent_trends": analyze_recent_performance_trends(analytics_videos),
            "alerts": generate_performance_alerts(analytics_videos)
        }
        
        return APIResponse(
            status="success",
            data=dashboard_data,
            message="Performance dashboard data retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error generating performance dashboard: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating dashboard: {str(e)}"
        )

@router.get("/api/v1/analytics/revenue-insights")
async def get_revenue_insights():
    """
    Get detailed revenue analytics and insights.
    
    Returns:
        APIResponse: Revenue insights data
    """
    try:
        videos = get_all_ideas()
        
        # Convert to analytics format with revenue focus
        analytics_videos = []
        for video in videos:
            views = video.get("expected_views", 0)
            analytics_video = {
                "title": video.get("title", ""),
                "category": video.get("category", "unknown"),
                "views": views,
                "revenue_total": views * 0.01,
                "ad_revenue": views * 0.004,
                "sponsorship_revenue": views * 0.004,
                "affiliate_revenue": views * 0.002,
                "published_at": video.get("created_at", "")
            }
            analytics_videos.append(analytics_video)
        
        # Generate revenue insights
        revenue_insights = {
            "revenue_overview": {
                "total_revenue": sum(v["revenue_total"] for v in analytics_videos),
                "revenue_per_video": mean([v["revenue_total"] for v in analytics_videos]) if analytics_videos else 0,
                "revenue_per_view": sum(v["revenue_total"] for v in analytics_videos) / sum(v["views"] for v in analytics_videos) if sum(v["views"] for v in analytics_videos) > 0 else 0
            },
            "revenue_streams": analyze_revenue_streams(analytics_videos),
            "revenue_forecast": forecast_revenue(analytics_videos),
            "monetization_opportunities": identify_monetization_opportunities(analytics_videos),
            "rpm_analysis": calculate_rpm_analysis(analytics_videos),
            "revenue_by_category": analyze_revenue_by_category(analytics_videos),
            "optimization_suggestions": generate_revenue_optimization_suggestions(analytics_videos)
        }
        
        return APIResponse(
            status="success",
            data=revenue_insights,
            message="Revenue insights generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error generating revenue insights: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating revenue insights: {str(e)}"
        )

@router.get("/api/v1/analytics/content-strategy")
async def get_content_strategy_analytics():
    """
    Get content strategy analytics and recommendations.
    
    Returns:
        APIResponse: Content strategy data
    """
    try:
        videos = get_all_ideas()
        
        # Convert to analytics format
        analytics_videos = []
        for video in videos:
            analytics_video = {
                "title": video.get("title", ""),
                "category": video.get("category", "unknown"),
                "views": video.get("expected_views", 0),
                "performance_score": min(video.get("expected_views", 0) / 100, 100),
                "engagement_score": 0.035,
                "duration": 600,  # Default 10 minutes
                "published_at": video.get("created_at", "")
            }
            analytics_videos.append(analytics_video)
        
        # Generate content strategy analytics
        strategy_data = {
            "content_performance": analyze_content_patterns(analytics_videos),
            "category_analysis": analyze_category_performance(analytics_videos),
            "optimal_content_length": analyze_optimal_content_length(analytics_videos),
            "posting_patterns": analyze_posting_patterns(analytics_videos),
            "content_recommendations": generate_content_recommendations(analytics_videos),
            "trending_topics": identify_trending_topics(analytics_videos),
            "content_gaps": identify_content_gaps(analytics_videos),
            "audience_preferences": analyze_audience_preferences(analytics_videos)
        }
        
        return APIResponse(
            status="success",
            data=strategy_data,
            message="Content strategy analytics generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error generating content strategy analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating content strategy: {str(e)}"
        )

@router.get("/api/v1/analytics/growth-metrics")
async def get_growth_metrics():
    """
    Get growth metrics and projections.
    
    Returns:
        APIResponse: Growth metrics data
    """
    try:
        videos = get_all_ideas()
        
        # Convert to analytics format
        analytics_videos = []
        for video in videos:
            analytics_video = {
                "views": video.get("expected_views", 0),
                "published_at": video.get("created_at", ""),
                "engagement_score": 0.035,
                "performance_score": min(video.get("expected_views", 0) / 100, 100)
            }
            analytics_videos.append(analytics_video)
        
        # Mock channel data
        channel_data = {
            "subscriber_count": 1000,
            "total_views": sum(v["views"] for v in analytics_videos),
            "channel_age_months": 6
        }
        
        # Generate growth metrics
        growth_data = {
            "current_metrics": calculate_current_growth_metrics(analytics_videos, channel_data),
            "growth_projections": calculate_audience_growth_metrics(analytics_videos, channel_data),
            "milestone_tracking": calculate_milestone_progress(channel_data),
            "growth_strategies": generate_growth_strategies(analytics_videos, channel_data),
            "benchmark_comparison": compare_growth_to_benchmarks(analytics_videos, channel_data),
            "growth_bottlenecks": identify_growth_bottlenecks(analytics_videos, channel_data)
        }
        
        return APIResponse(
            status="success",
            data=growth_data,
            message="Growth metrics generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error generating growth metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating growth metrics: {str(e)}"
        )

@router.get("/api/v1/analytics/predictive")
async def get_predictive_analytics():
    """
    Get predictive analytics and forecasts.
    
    Returns:
        APIResponse: Predictive analytics data
    """
    try:
        videos = get_all_ideas()
        
        # Convert to analytics format
        analytics_videos = []
        for video in videos:
            views = video.get("expected_views", 0)
            analytics_video = {
                "title": video.get("title", ""),
                "views": views,
                "performance_score": min(views / 100, 100),
                "engagement_score": 0.035,
                "revenue_total": views * 0.01,
                "published_at": video.get("created_at", "")
            }
            analytics_videos.append(analytics_video)
        
        # Generate predictive analytics
        predictions = {
            "performance_trends": predict_trends(analytics_videos),
            "revenue_forecasts": forecast_revenue(analytics_videos),
            "growth_predictions": predict_growth_trajectory(analytics_videos),
            "content_performance_predictions": predict_content_performance(analytics_videos),
            "market_trend_analysis": analyze_market_trends(analytics_videos),
            "risk_assessment": assess_performance_risks(analytics_videos),
            "opportunity_identification": identify_future_opportunities(analytics_videos),
            "confidence_metrics": calculate_prediction_confidence(analytics_videos)
        }
        
        return APIResponse(
            status="success",
            data=predictions,
            message="Predictive analytics generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error generating predictive analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating predictions: {str(e)}"
        )

@router.post("/api/v1/analytics/export")
async def export_analytics(
    format: str = Query("json", description="Export format: json, csv, txt"),
    include_predictions: bool = Query(True, description="Include predictive data"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    """
    Export analytics data in specified format.
    
    Args:
        format: Export format (json, csv, txt)
        include_predictions: Whether to include predictive analytics
        category: Filter by specific category
        
    Returns:
        APIResponse: Exported data
    """
    try:
        videos = get_all_ideas()
        
        # Convert and filter data
        analytics_videos = []
        for video in videos:
            if category and video.get("category", "").lower() != category.lower():
                continue
                
            views = video.get("expected_views", 0)
            analytics_video = {
                "title": video.get("title", ""),
                "category": video.get("category", "unknown"),
                "views": views,
                "performance_score": min(views / 100, 100),
                "revenue_total": views * 0.01,
                "published_at": video.get("created_at", "")
            }
            analytics_videos.append(analytics_video)
        
        # Generate comprehensive data
        export_data = {
            "overview": generate_analytics_overview(analytics_videos),
            "performance": analyze_performance_metrics(analytics_videos),
            "revenue": analyze_revenue_streams(analytics_videos),
            "content": analyze_content_patterns(analytics_videos)
        }
        
        if include_predictions:
            export_data["predictions"] = {
                "trends": predict_trends(analytics_videos),
                "revenue_forecast": forecast_revenue(analytics_videos)
            }
        
        # Export in requested format
        exported_content = export_analytics_data(export_data, format)
        
        return APIResponse(
            status="success",
            data={
                "format": format,
                "content": exported_content,
                "size": len(exported_content),
                "timestamp": datetime.utcnow().isoformat()
            },
            message=f"Analytics data exported successfully in {format} format"
        )
        
    except Exception as e:
        logger.error(f"Error exporting analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error exporting analytics: {str(e)}"
        )

# Helper functions for additional analytics
def analyze_revenue_by_category(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze revenue performance by category."""
    try:
        category_revenue = defaultdict(lambda: {"total": 0, "count": 0, "avg": 0})
        
        for video in videos:
            category = video.get("category", "unknown")
            revenue = video.get("revenue_total", 0)
            category_revenue[category]["total"] += revenue
            category_revenue[category]["count"] += 1
        
        # Calculate averages and sort by performance
        category_analysis = []
        for category, data in category_revenue.items():
            data["avg"] = data["total"] / data["count"] if data["count"] > 0 else 0
            category_analysis.append({
                "category": category,
                "total_revenue": round(data["total"], 2),
                "video_count": data["count"],
                "avg_revenue_per_video": round(data["avg"], 2),
                "revenue_share": round(data["total"] / sum(d["total"] for d in category_revenue.values()) * 100, 1) if sum(d["total"] for d in category_revenue.values()) > 0 else 0
            })
        
        return {
            "categories": sorted(category_analysis, key=lambda x: x["total_revenue"], reverse=True),
            "top_earning_category": max(category_analysis, key=lambda x: x["total_revenue"])["category"] if category_analysis else "none",
            "most_efficient_category": max(category_analysis, key=lambda x: x["avg_revenue_per_video"])["category"] if category_analysis else "none"
        }
        
    except Exception as e:
        logger.error(f"Error analyzing revenue by category: {str(e)}")
        return {}

def generate_revenue_optimization_suggestions(videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate revenue optimization suggestions."""
    try:
        suggestions = []
        
        if not videos:
            return [{
                "suggestion": "Create content to start generating revenue",
                "impact": "high",
                "effort": "high",
                "timeline": "1-3 months"
            }]
        
        # Analyze current revenue performance
        total_revenue = sum(v.get("revenue_total", 0) for v in videos)
        total_views = sum(v.get("views", 0) for v in videos)
        revenue_per_view = total_revenue / total_views if total_views > 0 else 0
        
        # Low RPV optimization
        if revenue_per_view < 0.005:
            suggestions.append({
                "suggestion": "Improve revenue per view through better monetization",
                "current_rpv": f"${revenue_per_view:.4f}",
                "target_rpv": "$0.01",
                "impact": "high",
                "effort": "medium",
                "timeline": "2-4 weeks",
                "actions": [
                    "Negotiate better ad rates",
                    "Add affiliate marketing",
                    "Seek sponsorship opportunities",
                    "Create premium content offerings"
                ]
            })
        
        # High-performing content optimization
        high_performers = [v for v in videos if v.get("views", 0) > mean([vid.get("views", 0) for vid in videos]) * 1.5]
        if high_performers:
            avg_revenue = mean([v.get("revenue_total", 0) for v in high_performers])
            suggestions.append({
                "suggestion": "Replicate success patterns from high-performing content",
                "high_performer_count": len(high_performers),
                "avg_revenue": f"${avg_revenue:.2f}",
                "impact": "medium",
                "effort": "low",
                "timeline": "1-2 weeks",
                "actions": [
                    "Analyze common elements in top videos",
                    "Create similar content",
                    "Apply same monetization strategies",
                    "Optimize titles and thumbnails"
                ]
            })
        
        # Diversification suggestions
        revenue_streams = {
            "ad_revenue": sum(v.get("ad_revenue", 0) for v in videos),
            "sponsorship_revenue": sum(v.get("sponsorship_revenue", 0) for v in videos),
            "affiliate_revenue": sum(v.get("affiliate_revenue", 0) for v in videos)
        }
        
        dominant_stream = max(revenue_streams, key=revenue_streams.get)
        if revenue_streams[dominant_stream] / total_revenue > 0.8:
            suggestions.append({
                "suggestion": "Diversify revenue streams to reduce dependency",
                "dominant_stream": dominant_stream.replace("_", " ").title(),
                "dependency_percentage": f"{revenue_streams[dominant_stream] / total_revenue * 100:.0f}%",
                "impact": "medium",
                "effort": "medium",
                "timeline": "4-8 weeks",
                "actions": [
                    "Explore additional monetization methods",
                    "Build email list for direct marketing",
                    "Create digital products",
                    "Develop membership programs"
                ]
            })
        
        return suggestions[:5]  # Return top 5 suggestions
        
    except Exception as e:
        logger.error(f"Error generating revenue optimization suggestions: {str(e)}")
        return []

def analyze_optimal_content_length(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze optimal content length based on performance."""
    try:
        if not videos:
            return {"error": "No video data available"}
        
        # Group videos by duration ranges
        duration_ranges = {
            "short": {"range": "0-5 min", "videos": [], "min": 0, "max": 300},
            "medium": {"range": "5-15 min", "videos": [], "min": 300, "max": 900},
            "long": {"range": "15+ min", "videos": [], "min": 900, "max": float('inf')}
        }
        
        for video in videos:
            duration = video.get("duration", 600)  # Default 10 minutes
            for range_key, range_data in duration_ranges.items():
                if range_data["min"] <= duration < range_data["max"]:
                    range_data["videos"].append(video)
                    break
        
        # Analyze performance by duration range
        range_analysis = []
        for range_key, range_data in duration_ranges.items():
            if range_data["videos"]:
                avg_views = mean([v.get("views", 0) for v in range_data["videos"]])
                avg_engagement = mean([v.get("engagement_score", 0) for v in range_data["videos"]])
                avg_performance = mean([v.get("performance_score", 0) for v in range_data["videos"]])
                
                range_analysis.append({
                    "duration_range": range_data["range"],
                    "video_count": len(range_data["videos"]),
                    "avg_views": int(avg_views),
                    "avg_engagement": round(avg_engagement, 4),
                    "avg_performance": round(avg_performance, 1),
                    "total_score": round((avg_views/1000 + avg_engagement*1000 + avg_performance)/3, 1)
                })
        
        # Find optimal range
        optimal_range = max(range_analysis, key=lambda x: x["total_score"]) if range_analysis else None
        
        return {
            "range_analysis": sorted(range_analysis, key=lambda x: x["total_score"], reverse=True),
            "optimal_range": optimal_range,
            "recommendation": f"Focus on {optimal_range['duration_range']} content for best performance" if optimal_range else "Create more content to determine optimal length"
        }
        
    except Exception as e:
        logger.error(f"Error analyzing optimal content length: {str(e)}")
        return {"error": str(e)}

def analyze_posting_patterns(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze posting patterns and their impact on performance."""
    try:
        if not videos:
            return {"error": "No video data available"}
        
        # Parse posting dates and analyze patterns
        posting_data = []
        for video in videos:
            pub_date = video.get("published_at", "")
            if pub_date:
                try:
                    if 'T' in pub_date:
                        date_obj = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                    else:
                        date_obj = datetime.strptime(pub_date, '%Y-%m-%d')
                    
                    posting_data.append({
                        "date": date_obj,
                        "day_of_week": date_obj.strftime('%A'),
                        "hour": date_obj.hour,
                        "views": video.get("views", 0),
                        "performance": video.get("performance_score", 0)
                    })
                except Exception:
                    continue
        
        if not posting_data:
            return {"error": "No valid posting date data"}
        
        # Analyze by day of week
        day_performance = defaultdict(lambda: {"views": [], "performance": []})
        for post in posting_data:
            day_performance[post["day_of_week"]]["views"].append(post["views"])
            day_performance[post["day_of_week"]]["performance"].append(post["performance"])
        
        day_analysis = []
        for day, data in day_performance.items():
            if data["views"]:
                day_analysis.append({
                    "day": day,
                    "avg_views": int(mean(data["views"])),
                    "avg_performance": round(mean(data["performance"]), 1),
                    "post_count": len(data["views"])
                })
        
        # Find best posting day
        best_day = max(day_analysis, key=lambda x: x["avg_performance"]) if day_analysis else None
        
        # Analyze posting frequency
        if len(posting_data) >= 2:
            sorted_posts = sorted(posting_data, key=lambda x: x["date"])
            intervals = []
            for i in range(1, len(sorted_posts)):
                interval = (sorted_posts[i]["date"] - sorted_posts[i-1]["date"]).days
                intervals.append(interval)
            
            avg_interval = mean(intervals) if intervals else 0
            frequency_analysis = {
                "avg_days_between_posts": round(avg_interval, 1),
                "posting_consistency": "consistent" if stdev(intervals) < 2 else "inconsistent" if len(intervals) > 1 else "unknown",
                "recommended_frequency": "3-4 days" if avg_interval > 7 else "maintain current pace"
            }
        else:
            frequency_analysis = {
                "avg_days_between_posts": 0,
                "posting_consistency": "insufficient_data",
                "recommended_frequency": "establish regular schedule"
            }
        
        return {
            "day_analysis": sorted(day_analysis, key=lambda x: x["avg_performance"], reverse=True),
            "best_posting_day": best_day,
            "frequency_analysis": frequency_analysis,
            "recommendations": [
                f"Post on {best_day['day']} for best performance" if best_day else "Collect more data to identify optimal posting day",
                f"Maintain {frequency_analysis['recommended_frequency']} posting schedule",
                "Monitor performance patterns over time"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error analyzing posting patterns: {str(e)}")
        return {"error": str(e)}

def identify_trending_topics(videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Identify trending topics based on recent performance."""
    try:
        if not videos:
            return []
        
        # Analyze recent videos (last 30% of content)
        sorted_videos = sorted(videos, key=lambda x: x.get("published_at", ""))
        recent_count = max(1, len(sorted_videos) // 3)
        recent_videos = sorted_videos[-recent_count:]
        
        # Extract topics from titles and categories
        trending_topics = []
        
        # Category trends
        category_performance = defaultdict(lambda: {"count": 0, "avg_performance": 0, "total_views": 0})
        for video in recent_videos:
            category = video.get("category", "unknown")
            category_performance[category]["count"] += 1
            category_performance[category]["avg_performance"] += video.get("performance_score", 0)
            category_performance[category]["total_views"] += video.get("views", 0)
        
        for category, data in category_performance.items():
            if data["count"] > 0:
                trending_topics.append({
                    "topic": category,
                    "type": "category",
                    "recent_videos": data["count"],
                    "avg_performance": round(data["avg_performance"] / data["count"], 1),
                    "total_views": data["total_views"],
                    "trend_strength": min(data["count"] * 20 + data["avg_performance"], 100)
                })
        
        # Title keyword analysis (simplified)
        common_words = defaultdict(int)
        for video in recent_videos:
            title = video.get("title", "").lower()
            words = [word.strip('.,!?()[]{}":;') for word in title.split() if len(word) > 3]
            for word in words:
                common_words[word] += 1
        
        # Add trending keywords
        for word, count in sorted(common_words.items(), key=lambda x: x[1], reverse=True)[:5]:
            if count >= 2:  # Appears in at least 2 videos
                trending_topics.append({
                    "topic": word,
                    "type": "keyword",
                    "recent_videos": count,
                    "avg_performance": 50,  # Default performance
                    "total_views": 0,
                    "trend_strength": min(count * 25, 100)
                })
        
        return sorted(trending_topics, key=lambda x: x["trend_strength"], reverse=True)[:10]
        
    except Exception as e:
        logger.error(f"Error identifying trending topics: {str(e)}")
        return []

def identify_content_gaps(videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Identify content gaps and opportunities."""
    try:
        gaps = []
        
        if not videos:
            return [{
                "gap_type": "foundation",
                "description": "No content created yet",
                "opportunity": "Start creating content in your niche",
                "priority": "critical"
            }]
        
        # Category gap analysis
        categories = [v.get("category", "unknown") for v in videos]
        category_counts = {cat: categories.count(cat) for cat in set(categories)}
        
        # Popular categories not covered
        popular_categories = ["tech", "gaming", "education", "entertainment", "lifestyle", "business"]
        missing_categories = [cat for cat in popular_categories if cat not in category_counts]
        
        for category in missing_categories[:3]:  # Top 3 missing
            gaps.append({
                "gap_type": "category",
                "description": f"No {category} content",
                "opportunity": f"Explore {category} content to diversify audience",
                "priority": "medium",
                "potential_impact": "audience_expansion"
            })
        
        # Performance gap analysis
        performance_scores = [v.get("performance_score", 0) for v in videos]
        avg_performance = mean(performance_scores)
        
        if avg_performance < 50:
            gaps.append({
                "gap_type": "quality",
                "description": "Overall content performance below average",
                "opportunity": "Focus on improving content quality and optimization",
                "priority": "high",
                "potential_impact": "performance_boost",
                "suggested_actions": [
                    "Analyze top-performing competitor content",
                    "Improve video production quality",
                    "Optimize titles and thumbnails",
                    "Enhance audience engagement strategies"
                ]
            })
        
        # Frequency gap analysis
        if len(videos) < 10:
            gaps.append({
                "gap_type": "volume",
                "description": "Low content volume",
                "opportunity": "Increase content creation frequency",
                "priority": "medium",
                "potential_impact": "audience_growth",
                "target": "Aim for 2-3 videos per week"
            })
        
        # Duration gap analysis
        durations = [v.get("duration", 600) for v in videos]
        avg_duration = mean(durations)
        
        if avg_duration < 300:  # Less than 5 minutes
            gaps.append({
                "gap_type": "depth",
                "description": "Content may be too short for in-depth coverage",
                "opportunity": "Create longer-form content for better engagement",
                "priority": "low",
                "potential_impact": "engagement_improvement"
            })
        elif avg_duration > 1200:  # More than 20 minutes
            gaps.append({
                "gap_type": "accessibility",
                "description": "Content may be too long for casual viewers",
                "opportunity": "Create shorter, more digestible content",
                "priority": "low",
                "potential_impact": "audience_retention"
            })
        
        # Engagement gap analysis
        engagement_scores = [v.get("engagement_score", 0) for v in videos]
        avg_engagement = mean(engagement_scores)
        
        if avg_engagement < 0.03:  # Less than 3%
            gaps.append({
                "gap_type": "engagement",
                "description": "Low audience engagement rates",
                "opportunity": "Implement strategies to boost viewer interaction",
                "priority": "high",
                "potential_impact": "community_building",
                "suggested_actions": [
                    "Add more calls-to-action",
                    "Ask questions to encourage comments",
                    "Create interactive content",
                    "Respond to comments actively"
                ]
            })
        
        return sorted(gaps, key=lambda x: {"critical": 4, "high": 3, "medium": 2, "low": 1}[x["priority"]], reverse=True)
        
    except Exception as e:
        logger.error(f"Error identifying content gaps: {str(e)}")
        return []

def analyze_audience_preferences(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze audience preferences based on content performance."""
    try:
        if not videos:
            return {"error": "No video data available for analysis"}
        
        preferences = {
            "content_types": {},
            "optimal_length": {},
            "preferred_topics": {},
            "engagement_patterns": {},
            "viewing_behavior": {}
        }
        
        # Content type preferences
        category_performance = defaultdict(lambda: {"views": [], "engagement": [], "performance": []})
        for video in videos:
            category = video.get("category", "unknown")
            category_performance[category]["views"].append(video.get("views", 0))
            category_performance[category]["engagement"].append(video.get("engagement_score", 0))
            category_performance[category]["performance"].append(video.get("performance_score", 0))
        
        content_preferences = []
        for category, data in category_performance.items():
            if data["views"]:
                content_preferences.append({
                    "category": category,
                    "avg_views": int(mean(data["views"])),
                    "avg_engagement": round(mean(data["engagement"]), 4),
                    "avg_performance": round(mean(data["performance"]), 1),
                    "preference_score": round((mean(data["views"])/1000 + mean(data["engagement"])*1000 + mean(data["performance"]))/3, 1)
                })
        
        preferences["content_types"] = sorted(content_preferences, key=lambda x: x["preference_score"], reverse=True)
        
        # Length preferences
        duration_ranges = {
            "short": [v for v in videos if v.get("duration", 600) < 300],
            "medium": [v for v in videos if 300 <= v.get("duration", 600) < 900],
            "long": [v for v in videos if v.get("duration", 600) >= 900]
        }
        
        length_preferences = []
        for length_type, video_list in duration_ranges.items():
            if video_list:
                avg_performance = mean([v.get("performance_score", 0) for v in video_list])
                avg_engagement = mean([v.get("engagement_score", 0) for v in video_list])
                length_preferences.append({
                    "length_type": length_type,
                    "video_count": len(video_list),
                    "avg_performance": round(avg_performance, 1),
                    "avg_engagement": round(avg_engagement, 4),
                    "preference_indicator": round(avg_performance + avg_engagement * 1000, 1)
                })
        
        preferences["optimal_length"] = sorted(length_preferences, key=lambda x: x["preference_indicator"], reverse=True)
        
        # Topic preferences (from titles)
        title_words = []
        for video in videos:
            title = video.get("title", "").lower()
            words = [word.strip('.,!?()[]{}":;') for word in title.split() if len(word) > 3]
            for word in words:
                title_words.append((word, video.get("performance_score", 0)))
        
        word_performance = defaultdict(list)
        for word, performance in title_words:
            word_performance[word].append(performance)
        
        topic_preferences = []
        for word, performances in word_performance.items():
            if len(performances) >= 2:  # Word appears in at least 2 videos
                topic_preferences.append({
                    "topic": word,
                    "frequency": len(performances),
                    "avg_performance": round(mean(performances), 1),
                    "preference_score": round(mean(performances) * len(performances) / 10, 1)
                })
        
        preferences["preferred_topics"] = sorted(topic_preferences, key=lambda x: x["preference_score"], reverse=True)[:10]
        
        # Engagement patterns
        high_engagement_videos = [v for v in videos if v.get("engagement_score", 0) > mean([vid.get("engagement_score", 0) for vid in videos])]
        
        if high_engagement_videos:
            engagement_patterns = {
                "high_engagement_count": len(high_engagement_videos),
                "common_categories": list(set([v.get("category", "unknown") for v in high_engagement_videos])),
                "avg_duration": round(mean([v.get("duration", 600) for v in high_engagement_videos]) / 60, 1),
                "characteristics": [
                    "Interactive content performs better" if len(high_engagement_videos) > len(videos) * 0.3 else "Focus on engagement strategies",
                    f"Optimal duration around {round(mean([v.get('duration', 600) for v in high_engagement_videos]) / 60, 1)} minutes",
                    f"Categories: {', '.join(list(set([v.get('category', 'unknown') for v in high_engagement_videos]))[:3])}"
                ]
            }
        else:
            engagement_patterns = {
                "high_engagement_count": 0,
                "common_categories": [],
                "avg_duration": 0,
                "characteristics": ["Need to improve overall engagement"]
            }
        
        preferences["engagement_patterns"] = engagement_patterns
        
        # Viewing behavior insights
        total_views = sum(v.get("views", 0) for v in videos)
        total_videos = len(videos)
        
        viewing_behavior = {
            "avg_views_per_video": int(total_views / total_videos) if total_videos > 0 else 0,
            "view_distribution": "consistent" if stdev([v.get("views", 0) for v in videos]) < mean([v.get("views", 0) for v in videos]) else "variable",
            "audience_loyalty": round(mean([v.get("engagement_score", 0) for v in videos]) * 100, 1),
            "growth_indicator": "positive" if len(videos) > 1 and videos[-1].get("views", 0) > videos[0].get("views", 0) else "stable"
        }
        
        preferences["viewing_behavior"] = viewing_behavior
        
        return preferences
        
    except Exception as e:
        logger.error(f"Error analyzing audience preferences: {str(e)}")
        return {"error": str(e)}

def predict_growth_trajectory(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Predict future growth trajectory based on current trends."""
    try:
        if len(videos) < 3:
            return {
                "error": "Insufficient data for growth prediction",
                "recommendation": "Create more content to enable growth forecasting"
            }
        
        # Sort videos by date
        sorted_videos = sorted(videos, key=lambda x: x.get("published_at", ""))
        
        # Calculate growth metrics
        view_progression = [v.get("views", 0) for v in sorted_videos]
        performance_progression = [v.get("performance_score", 0) for v in sorted_videos]
        
        # Calculate growth rates
        view_growth_rates = []
        performance_growth_rates = []
        
        for i in range(1, len(view_progression)):
            if view_progression[i-1] > 0:
                view_growth = (view_progression[i] - view_progression[i-1]) / view_progression[i-1]
                view_growth_rates.append(view_growth)
            
            if performance_progression[i-1] > 0:
                perf_growth = (performance_progression[i] - performance_progression[i-1]) / performance_progression[i-1]
                performance_growth_rates.append(perf_growth)
        
        # Calculate average growth rates
        avg_view_growth = mean(view_growth_rates) if view_growth_rates else 0
        avg_performance_growth = mean(performance_growth_rates) if performance_growth_rates else 0
        
        # Project future performance
        current_avg_views = mean(view_progression[-3:]) if len(view_progression) >= 3 else view_progression[-1]
        current_avg_performance = mean(performance_progression[-3:]) if len(performance_progression) >= 3 else performance_progression[-1]
        
        # Generate 6-month projections
        monthly_projections = []
        projected_views = current_avg_views
        projected_performance = current_avg_performance
        
        for month in range(1, 7):
            projected_views *= (1 + avg_view_growth)
            projected_performance *= (1 + avg_performance_growth)
            
            # Apply realistic constraints
            projected_views = max(0, min(projected_views, current_avg_views * 5))  # Max 5x growth
            projected_performance = max(0, min(projected_performance, 100))  # Max 100 performance score
            
            monthly_projections.append({
                "month": month,
                "projected_avg_views": int(projected_views),
                "projected_performance": round(projected_performance, 1),
                "confidence": max(90 - month * 10, 30)  # Decreasing confidence over time
            })
        
        # Determine growth trajectory
        if avg_view_growth > 0.1:
            trajectory = "rapid_growth"
            trajectory_description = "Strong upward trajectory with rapid growth potential"
        elif avg_view_growth > 0.05:
            trajectory = "steady_growth"
            trajectory_description = "Consistent steady growth pattern"
        elif avg_view_growth > 0:
            trajectory = "slow_growth"
            trajectory_description = "Gradual growth with room for improvement"
        else:
            trajectory = "stagnant"
            trajectory_description = "Growth has stalled, intervention needed"
        
        # Growth factors analysis
        growth_factors = {
            "content_consistency": "positive" if len(videos) >= 5 else "needs_improvement",
            "performance_trend": "improving" if avg_performance_growth > 0 else "declining",
            "audience_engagement": "good" if mean([v.get("engagement_score", 0) for v in videos]) > 0.03 else "needs_work",
            "content_quality": "high" if mean(performance_progression) > 70 else "moderate" if mean(performance_progression) > 40 else "low"
        }
        
        return {
            "trajectory_type": trajectory,
            "trajectory_description": trajectory_description,
            "growth_metrics": {
                "avg_view_growth_rate": round(avg_view_growth * 100, 1),
                "avg_performance_growth_rate": round(avg_performance_growth * 100, 1),
                "current_momentum": "positive" if avg_view_growth > 0 and avg_performance_growth > 0 else "mixed" if avg_view_growth > 0 or avg_performance_growth > 0 else "negative"
            },
            "monthly_projections": monthly_projections,
            "growth_factors": growth_factors,
            "recommendations": generate_growth_recommendations(trajectory, growth_factors),
            "milestone_predictions": predict_growth_milestones(current_avg_views, avg_view_growth)
        }
        
    except Exception as e:
        logger.error(f"Error predicting growth trajectory: {str(e)}")
        return {"error": str(e)}

def generate_growth_recommendations(trajectory: str, growth_factors: Dict[str, str]) -> List[str]:
    """Generate growth recommendations based on trajectory and factors."""
    recommendations = []
    
    if trajectory == "rapid_growth":
        recommendations.extend([
            "Maintain current content strategy and quality",
            "Scale up content production to capitalize on momentum",
            "Invest in better equipment and production quality",
            "Consider collaborations to expand reach"
        ])
    elif trajectory == "steady_growth":
        recommendations.extend([
            "Continue consistent posting schedule",
            "Experiment with new content formats",
            "Focus on audience engagement and community building",
            "Optimize content for search and discovery"
        ])
    elif trajectory == "slow_growth":
        recommendations.extend([
            "Analyze and replicate successful content patterns",
            "Improve content quality and production value",
            "Increase posting frequency if possible",
            "Focus on trending topics and keywords"
        ])
    else:  # stagnant
        recommendations.extend([
            "Conduct comprehensive content audit",
            "Pivot content strategy based on audience feedback",
            "Invest in learning new content creation skills",
            "Consider rebranding or niche adjustment"
        ])
    
    # Add factor-specific recommendations
    if growth_factors.get("content_consistency") == "needs_improvement":
        recommendations.append("Establish and maintain regular posting schedule")
    
    if growth_factors.get("audience_engagement") == "needs_work":
        recommendations.append("Implement stronger calls-to-action and engagement strategies")
    
    if growth_factors.get("content_quality") == "low":
        recommendations.append("Focus on improving video production quality and storytelling")
    return recommendations[:6]  # Return top 6 recommendations

def predict_growth_milestones(current_views: float, growth_rate: float) -> List[Dict[str, Any]]:
    """Predict when growth milestones will be reached."""
    milestones = [1000, 5000, 10000, 50000, 100000, 500000, 1000000]
    predictions = []
    
    if growth_rate <= 0:
        return [{
            "milestone": "Growth stalled",
            "message": "Focus on improving content to restart growth",
            "timeline": "immediate_action_needed"
        }]
    
    for milestone in milestones:
        if current_views < milestone:
            # Calculate months to reach milestone
            months_to_milestone = math.log(milestone / current_views) / math.log(1 + growth_rate)
            
            if months_to_milestone <= 24:  # Only predict within 2 years
                predictions.append({
                    "milestone": f"{milestone:,} average views",
                    "estimated_months": round(months_to_milestone, 1),
                    "confidence": max(90 - months_to_milestone * 2, 20),
                    "timeline": "short_term" if months_to_milestone <= 6 else "medium_term" if months_to_milestone <= 12 else "long_term"
                })
            
            if len(predictions) >= 3:  # Limit to 3 nearest milestones
                break
    
    return predictions

def predict_content_performance(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Predict performance of future content based on patterns."""
    try:
        if len(videos) < 3:
            return {"error": "Insufficient data for content performance prediction"}
        
        # Analyze performance patterns by category
        category_patterns = defaultdict(lambda: {"performances": [], "views": []})
        for video in videos:
            category = video.get("category", "unknown")
            category_patterns[category]["performances"].append(video.get("performance_score", 0))
            category_patterns[category]["views"].append(video.get("views", 0))
        
        # Generate predictions for each category
        category_predictions = []
        for category, data in category_patterns.items():
            if len(data["performances"]) >= 2:
                avg_performance = mean(data["performances"])
                performance_trend = "improving" if data["performances"][-1] > data["performances"][0] else "declining"
                
                # Predict next video performance in this category
                if len(data["performances"]) >= 3:
                    recent_trend = mean(data["performances"][-2:]) - mean(data["performances"][-3:-1])
                    predicted_performance = max(0, min(100, data["performances"][-1] + recent_trend))
                else:
                    predicted_performance = avg_performance
                
                category_predictions.append({
                    "category": category,
                    "predicted_performance": round(predicted_performance, 1),
                    "predicted_views": int(mean(data["views"]) * (predicted_performance / avg_performance)) if avg_performance > 0 else int(mean(data["views"])),
                    "confidence": min(90, len(data["performances"]) * 20),
                    "trend": performance_trend,
                    "recommendation": "focus" if predicted_performance > 60 else "improve" if predicted_performance > 30 else "reconsider"
                })
        
        # Overall performance prediction
        all_performances = [v.get("performance_score", 0) for v in videos]
        recent_performances = all_performances[-3:] if len(all_performances) >= 3 else all_performances
        
        if len(recent_performances) >= 2:
            performance_velocity = (recent_performances[-1] - recent_performances[0]) / len(recent_performances)
            next_predicted_performance = max(0, min(100, recent_performances[-1] + performance_velocity))
        else:
            next_predicted_performance = mean(all_performances)
        
        # Success probability analysis
        high_performers = [v for v in videos if v.get("performance_score", 0) > 70]
        success_rate = len(high_performers) / len(videos) if videos else 0
        
        return {
            "overall_prediction": {
                "next_video_performance": round(next_predicted_performance, 1),
                "success_probability": round(success_rate * 100, 1),
                "confidence": min(85, len(videos) * 15),
                "trend_direction": "upward" if performance_velocity > 0 else "downward" if performance_velocity < 0 else "stable"
            },
            "category_predictions": sorted(category_predictions, key=lambda x: x["predicted_performance"], reverse=True),
            "optimization_suggestions": [
                f"Focus on {category_predictions[0]['category']} content" if category_predictions and category_predictions[0]["predicted_performance"] > 60 else "Improve content quality across all categories",
                "Maintain consistent posting schedule",
                "Monitor performance trends closely",
                f"Success rate is {round(success_rate * 100, 1)}% - {'maintain current strategy' if success_rate > 0.5 else 'consider strategy adjustment'}"
            ],
            "risk_factors": identify_performance_risks(videos)
        }
        
    except Exception as e:
        logger.error(f"Error predicting content performance: {str(e)}")
        return {"error": str(e)}

def analyze_market_trends(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze market trends and their impact on content performance."""
    try:
        # Simulate market trend analysis (in real implementation, this would use external data)
        market_trends = {
            "trending_categories": [
                {"category": "tech", "growth": 15.2, "competition": "high"},
                {"category": "gaming", "growth": 12.8, "competition": "very_high"},
                {"category": "education", "growth": 18.5, "competition": "medium"},
                {"category": "lifestyle", "growth": 8.3, "competition": "high"},
                {"category": "business", "growth": 22.1, "competition": "medium"}
            ],
            "content_format_trends": [
                {"format": "short_form", "popularity": 85, "growth_rate": 25.3},
                {"format": "tutorials", "popularity": 78, "growth_rate": 12.1},
                {"format": "reviews", "popularity": 65, "growth_rate": 5.8},
                {"format": "vlogs", "popularity": 45, "growth_rate": -2.3}
            ],
            "seasonal_patterns": {
                "current_season": "general",
                "peak_months": ["January", "September", "December"],
                "low_months": ["June", "July", "August"],
                "seasonal_adjustment": 1.0
            }
        }
        
        # Analyze user's content against market trends
        user_categories = [v.get("category", "unknown") for v in videos]
        category_distribution = {cat: user_categories.count(cat) for cat in set(user_categories)}
        
        # Market alignment analysis
        alignment_score = 0
        category_recommendations = []
        
        for trend_cat in market_trends["trending_categories"]:
            category = trend_cat["category"]
            if category in category_distribution:
                # User has content in trending category
                alignment_score += trend_cat["growth"] * (category_distribution[category] / len(videos))
                category_recommendations.append({
                    "category": category,
                    "status": "aligned",
                    "recommendation": f"Increase {category} content - growing at {trend_cat['growth']}%",
                    "priority": "high" if trend_cat["growth"] > 15 else "medium"
                })
            else:
                # User missing trending category
                category_recommendations.append({
                    "category": category,
                    "status": "opportunity",
                    "recommendation": f"Consider adding {category} content - growing at {trend_cat['growth']}%",
                    "priority": "medium" if trend_cat["competition"] != "very_high" else "low"
                })
        
        # Competitive landscape analysis
        user_performance = mean([v.get("performance_score", 0) for v in videos]) if videos else 0
        market_position = (
            "leader" if user_performance > 80 else
            "competitive" if user_performance > 60 else
            "developing" if user_performance > 40 else
            "emerging"
        )
        
        return {
            "market_alignment_score": round(alignment_score, 1),
            "market_position": market_position,
            "trending_categories": market_trends["trending_categories"],
            "format_trends": market_trends["content_format_trends"],
            "category_recommendations": sorted(category_recommendations, key=lambda x: {"high": 3, "medium": 2, "low": 1}[x["priority"]], reverse=True),
            "competitive_insights": {
                "market_saturation": "high" if len(set(user_categories)) > 3 else "medium",
                "differentiation_opportunity": "focus_niche" if len(set(user_categories)) == 1 else "diversify",
                "competitive_advantage": analyze_competitive_advantage(videos, market_trends)
            },
            "seasonal_recommendations": generate_seasonal_recommendations(market_trends["seasonal_patterns"]),
            "market_opportunities": identify_market_opportunities(videos, market_trends)
        }
        
    except Exception as e:
        logger.error(f"Error analyzing market trends: {str(e)}")
        return {"error": str(e)}

def analyze_competitive_advantage(videos: List[Dict[str, Any]], market_trends: Dict[str, Any]) -> List[str]:
    """Analyze competitive advantages based on content and market data."""
    advantages = []
    
    if not videos:
        return ["Establish content presence to build competitive advantage"]
    
    # Performance advantage
    avg_performance = mean([v.get("performance_score", 0) for v in videos])
    if avg_performance > 70:
        advantages.append("High-quality content production")
    
    # Consistency advantage
    if len(videos) >= 5:
        advantages.append("Consistent content creation")
    
    # Niche focus advantage
    categories = [v.get("category", "unknown") for v in videos]
    if len(set(categories)) <= 2 and len(videos) >= 3:
        advantages.append("Strong niche focus and expertise")
    
    # Engagement advantage
    avg_engagement = mean([v.get("engagement_score", 0) for v in videos])
    if avg_engagement > 0.04:
        advantages.append("Strong audience engagement")
    
    return advantages if advantages else ["Opportunity to develop competitive advantages"]

def generate_seasonal_recommendations(seasonal_data: Dict[str, Any]) -> List[str]:
    """Generate seasonal content recommendations."""
    current_month = datetime.now().strftime("%B")
    
    recommendations = []
    
    if current_month in seasonal_data.get("peak_months", []):
        recommendations.extend([
            "Peak season - increase content production",
            "Focus on high-performing content types",
            "Capitalize on increased audience activity"
        ])
    elif current_month in seasonal_data.get("low_months", []):
        recommendations.extend([
            "Low season - focus on content planning",
            "Experiment with new content formats",
            "Build content backlog for peak seasons"
        ])
    else:
        recommendations.extend([
            "Maintain steady content production",
            "Prepare for upcoming seasonal changes",
            "Monitor seasonal performance patterns"
        ])
    
    return recommendations

def identify_market_opportunities(videos: List[Dict[str, Any]], market_trends: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Identify market opportunities based on content and trends."""
    opportunities = []
    
    # Category opportunities
    user_categories = set([v.get("category", "unknown") for v in videos])
    trending_categories = [t["category"] for t in market_trends.get("trending_categories", [])]
    
    for trend_cat in market_trends.get("trending_categories", []):
        if trend_cat["category"] not in user_categories and trend_cat["competition"] != "very_high":
            opportunities.append({
                "type": "category_expansion",
                "opportunity": f"Enter {trend_cat['category']} market",
                "growth_potential": trend_cat["growth"],
                "competition_level": trend_cat["competition"],
                "priority": "high" if trend_cat["growth"] > 15 and trend_cat["competition"] == "medium" else "medium"
            })
    
    # Format opportunities
    for format_trend in market_trends.get("content_format_trends", []):
        if format_trend["growth_rate"] > 10:
            opportunities.append({
                "type": "format_innovation",
                "opportunity": f"Adopt {format_trend['format']} content format",
                "growth_potential": format_trend["growth_rate"],
                "popularity": format_trend["popularity"],
                "priority": "high" if format_trend["growth_rate"] > 20 else "medium"
            })
    
    return sorted(opportunities, key=lambda x: {"high": 3, "medium": 2, "low": 1}[x["priority"]], reverse=True)[:5]

def assess_performance_risks(videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Assess potential risks to performance."""
    risks = []
    
    if not videos:
        return [{
            "risk_type": "no_content",
            "description": "No content created",
            "severity": "critical",
            "mitigation": "Start creating content immediately"
        }]
    
    # Performance decline risk
    if len(videos) >= 3:
        recent_performance = mean([v.get("performance_score", 0) for v in videos[-2:]])
        older_performance = mean([v.get("performance_score", 0) for v in videos[:-2]])
        
        if recent_performance < older_performance * 0.8:
            risks.append({
                "risk_type": "performance_decline",
                "description": "Recent content underperforming",
                "severity": "high",
                "impact": f"{((older_performance - recent_performance) / older_performance * 100):.1f}% performance drop",
                "mitigation": "Analyze successful content patterns and adjust strategy"
            })
    
    # Low engagement risk
    avg_engagement = mean([v.get("engagement_score", 0) for v in videos])
    if avg_engagement < 0.02:
        risks.append({
            "risk_type": "low_engagement",
            "description": "Below-average audience engagement",
            "severity": "medium",
            "impact": "Limited organic reach and growth",
            "mitigation": "Implement engagement strategies and community building"
        })
    
    # Content inconsistency risk
    if len(videos) < 5:
        risks.append({
            "risk_type": "inconsistent_posting",
            "description": "Irregular content creation",
            "severity": "medium",
            "impact": "Audience retention and algorithm performance",
            "mitigation": "Establish regular posting schedule"
        })
    
    # Category saturation risk
    categories = [v.get("category", "unknown") for v in videos]
    if len(set(categories)) == 1 and len(videos) >= 5:
        risks.append({
            "risk_type": "over_specialization",
            "description": "Limited content diversity",
            "severity": "low",
            "impact": "Reduced audience growth potential",
            "mitigation": "Consider expanding to related content categories"
        })
    
    # Performance stagnation risk
    performance_scores = [v.get("performance_score", 0) for v in videos]
    if len(performance_scores) >= 4:
        recent_variance = stdev(performance_scores[-4:]) if len(performance_scores) >= 4 else 0
        if recent_variance < 5:  # Very low variance indicates stagnation
            risks.append({
                "risk_type": "performance_stagnation",
                "description": "Performance metrics showing little variation",
                "severity": "medium",
                "impact": "Limited growth and optimization opportunities",
                "mitigation": "Experiment with new content formats and strategies"
            })
    
    return sorted(risks, key=lambda x: {"critical": 4, "high": 3, "medium": 2, "low": 1}[x["severity"]], reverse=True)

def identify_future_opportunities(videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Identify future opportunities for growth and optimization."""
    opportunities = []
    
    if not videos:
        return [{
            "opportunity_type": "foundation",
            "title": "Content Creation Foundation",
            "description": "Establish consistent content creation process",
            "potential_impact": "high",
            "timeline": "immediate",
            "effort_required": "high"
        }]
    
    # High-performing content scaling opportunity
    high_performers = [v for v in videos if v.get("performance_score", 0) > 70]
    if high_performers:
        common_categories = list(set([v.get("category", "unknown") for v in high_performers]))
        opportunities.append({
            "opportunity_type": "scaling",
            "title": "Scale High-Performing Content",
            "description": f"Increase production in successful categories: {', '.join(common_categories)}",
            "potential_impact": "high",
            "timeline": "short_term",
            "effort_required": "medium",
            "success_indicators": [
                f"{len(high_performers)} videos already performing well",
                f"Average performance: {mean([v.get('performance_score', 0) for v in high_performers]):.1f}"
            ]
        })
    
    # Monetization optimization opportunity
    total_views = sum(v.get("views", 0) for v in videos)
    if total_views > 10000:
        opportunities.append({
            "opportunity_type": "monetization",
            "title": "Advanced Monetization Strategies",
            "description": "Implement additional revenue streams beyond basic monetization",
            "potential_impact": "medium",
            "timeline": "medium_term",
            "effort_required": "medium",
            "revenue_potential": f"${total_views * 0.005:.2f} - ${total_views * 0.015:.2f} additional monthly revenue"
        })
    
    # Audience expansion opportunity
    categories = list(set([v.get("category", "unknown") for v in videos]))
    if len(categories) <= 2:
        opportunities.append({
            "opportunity_type": "expansion",
            "title": "Audience Diversification",
            "description": "Expand into complementary content categories",
            "potential_impact": "high",
            "timeline": "medium_term",
            "effort_required": "high",
            "growth_potential": "30-50% audience increase"
        })
    
    # Content quality enhancement opportunity
    avg_performance = mean([v.get("performance_score", 0) for v in videos])
    if avg_performance < 60:
        opportunities.append({
            "opportunity_type": "quality_improvement",
            "title": "Content Quality Enhancement",
            "description": "Invest in production quality and content optimization",
            "potential_impact": "high",
            "timeline": "short_term",
            "effort_required": "medium",
            "performance_boost": f"Potential {60 - avg_performance:.1f} point performance increase"
        })
    
    # Community building opportunity
    avg_engagement = mean([v.get("engagement_score", 0) for v in videos])
    if avg_engagement < 0.05:
        opportunities.append({
            "opportunity_type": "community",
            "title": "Community Building Initiative",
            "description": "Develop stronger audience relationships and engagement",
            "potential_impact": "medium",
            "timeline": "long_term",
            "effort_required": "high",
            "engagement_boost": f"Target {0.05 - avg_engagement:.3f} engagement rate increase"
        })
    
    # Collaboration opportunity
    if len(videos) >= 10 and avg_performance > 50:
        opportunities.append({
            "opportunity_type": "collaboration",
            "title": "Strategic Collaborations",
            "description": "Partner with other creators for cross-promotion",
            "potential_impact": "medium",
            "timeline": "medium_term",
            "effort_required": "low",
            "network_effect": "Exponential audience growth potential"
        })
    
    return sorted(opportunities, key=lambda x: {"high": 3, "medium": 2, "low": 1}[x["potential_impact"]], reverse=True)[:6]

def calculate_prediction_confidence(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate confidence metrics for predictions."""
    try:
        if not videos:
            return {
                "overall_confidence": 0,
                "data_quality": "insufficient",
                "prediction_reliability": "low",
                "factors": ["No data available for analysis"]
            }
        
        confidence_factors = {
            "data_volume": min(len(videos) / 10 * 100, 100),  # Max confidence at 10+ videos
            "data_consistency": 100 - (stdev([v.get("performance_score", 0) for v in videos]) * 2),  # Lower variance = higher confidence
            "temporal_coverage": min(len(videos) / 5 * 100, 100),  # Max confidence at 5+ time points
            "performance_stability": 100 - abs(mean([v.get("performance_score", 0) for v in videos[-3:]]) - mean([v.get("performance_score", 0) for v in videos[:-3]])) if len(videos) >= 6 else 50
        }
        
        # Ensure all factors are between 0 and 100
        for factor in confidence_factors:
            confidence_factors[factor] = max(0, min(100, confidence_factors[factor]))
        
        overall_confidence = mean(list(confidence_factors.values()))
        
        # Determine confidence level
        if overall_confidence >= 80:
            confidence_level = "high"
            reliability = "very_reliable"
        elif overall_confidence >= 60:
            confidence_level = "medium"
            reliability = "moderately_reliable"
        elif overall_confidence >= 40:
            confidence_level = "low"
            reliability = "limited_reliability"
        else:
            confidence_level = "very_low"
            reliability = "unreliable"
        
        # Generate confidence improvement suggestions
        improvement_suggestions = []
        if confidence_factors["data_volume"] < 70:
            improvement_suggestions.append("Create more content to improve prediction accuracy")
        if confidence_factors["data_consistency"] < 70:
            improvement_suggestions.append("Focus on consistent content quality")
        if confidence_factors["temporal_coverage"] < 70:
            improvement_suggestions.append("Maintain regular posting schedule for better trend analysis")
        
        return {
            "overall_confidence": round(overall_confidence, 1),
            "confidence_level": confidence_level,
            "prediction_reliability": reliability,
            "confidence_factors": {k: round(v, 1) for k, v in confidence_factors.items()},
            "improvement_suggestions": improvement_suggestions,
            "data_quality_score": round(mean([confidence_factors["data_volume"], confidence_factors["temporal_coverage"]]), 1),
            "prediction_accuracy_estimate": f"{max(50, overall_confidence):.0f}%"
        }
        
    except Exception as e:
        logger.error(f"Error calculating prediction confidence: {str(e)}")
        return {"error": str(e)}

def export_analytics_data(data: Dict[str, Any], format: str) -> str:
    """Export analytics data in specified format."""
    try:
        if format.lower() == "json":
            return json.dumps(data, indent=2, default=str)
        
        elif format.lower() == "csv":
            # Convert nested data to flat CSV format
            csv_data = []
            
            # Extract overview data
            if "overview" in data:
                overview = data["overview"]
                csv_data.append(["Metric", "Value"])
                for key, value in overview.items():
                    csv_data.append([key.replace("_", " ").title(), str(value)])
            
            # Convert to CSV string
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerows(csv_data)
            return output.getvalue()
        
        elif format.lower() == "txt":
            # Convert to readable text format
            text_output = []
            text_output.append("ANALYTICS REPORT")
            text_output.append("=" * 50)
            text_output.append("")
            
            for section, section_data in data.items():
                text_output.append(f"{section.replace('_', ' ').title()}:")
                text_output.append("-" * 30)
                
                if isinstance(section_data, dict):
                    for key, value in section_data.items():
                        text_output.append(f"  {key.replace('_', ' ').title()}: {value}")
                elif isinstance(section_data, list):
                    for i, item in enumerate(section_data, 1):
                        text_output.append(f"  {i}. {item}")
                else:
                    text_output.append(f"  {section_data}")
                
                text_output.append("")
            
            return "\n".join(text_output)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    except Exception as e:
        logger.error(f"Error exporting analytics data: {str(e)}")
        return f"Error exporting data: {str(e)}"

# Utility functions
def mean(values: List[float]) -> float:
    """Calculate mean of a list of values."""
    return sum(values) / len(values) if values else 0

def stdev(values: List[float]) -> float:
    """Calculate standard deviation of a list of values."""
    if len(values) < 2:
        return 0
    mean_val = mean(values)
    variance = sum((x - mean_val) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)

# Add router to main application
def setup_advanced_analytics_routes(app):
    """Setup advanced analytics routes in the main application."""
    app.include_router(router, prefix="/api/v1/advanced-analytics", tags=["Advanced Analytics"])