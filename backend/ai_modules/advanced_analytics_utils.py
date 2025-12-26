<UPDATED_CODE>"""
Utility functions for advanced analytics module.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import json
import csv
import io
import logging
from statistics import mean, median, stdev

logger = logging.getLogger(__name__)


def normalize_video_data(videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalize video data by calculating derived metrics and ensuring consistent format.
    
    Args:
        videos: List of video data dictionaries
        
    Returns:
        List of normalized video data with calculated metrics
    """
    normalized_videos = []
    
    for video in videos:
        normalized_video = video.copy()
        
        # Calculate engagement score
        views = video.get('views', 0)
        likes = video.get('likes', 0)
        comments = video.get('comments', 0)
        shares = video.get('shares', 0)
        
        if views > 0:
            engagement_score = (likes + comments + shares) / views
        else:
            engagement_score = 0
        
        normalized_video['engagement_score'] = engagement_score
        
        # Calculate total revenue
        ad_revenue = video.get('ad_revenue', 0)
        sponsorship_revenue = video.get('sponsorship_revenue', 0)
        affiliate_revenue = video.get('affiliate_revenue', 0)
        
        normalized_video['revenue_total'] = ad_revenue + sponsorship_revenue + affiliate_revenue
        
        # Calculate performance score
        normalized_video['performance_score'] = calculate_video_performance_score(normalized_video)
        
        # Ensure required fields exist
        normalized_video.setdefault('duration', 0)
        normalized_video.setdefault('category', 'unknown')
        normalized_video.setdefault('published_at', datetime.now().isoformat())
        
        normalized_videos.append(normalized_video)
    
    return normalized_videos


def calculate_video_performance_score(video: Dict[str, Any]) -> float:
    """
    Calculate a comprehensive performance score for a video.
    
    Args:
        video: Video data dictionary
        
    Returns:
        Performance score (0-100)
    """
    try:
        # Weights for different metrics
        weights = {
            'views': 0.3,
            'engagement': 0.25,
            'revenue': 0.25,
            'retention': 0.2
        }
        
        # Normalize metrics to 0-100 scale
        views_score = min(video.get('views', 0) / 1000, 100)  # 1000 views = 1 point
        engagement_score = min(video.get('engagement_score', 0) * 1000, 100)  # 10% engagement = 100 points
        revenue_score = min(video.get('revenue_total', 0) / 10, 100)  # $10 = 1 point
        
        # Estimate retention score (would use actual data in production)
        duration = video.get('duration', 0)
        if duration > 0:
            # Assume longer videos have better retention if they have good engagement
            retention_score = min(video.get('engagement_score', 0) * duration / 10, 100)
        else:
            retention_score = 0
        
        # Calculate weighted score
        total_score = (
            views_score * weights['views'] +
            engagement_score * weights['engagement'] +
            revenue_score * weights['revenue'] +
            retention_score * weights['retention']
        )
        
        return min(total_score, 100)
        
    except Exception as e:
        logger.error(f"Error calculating performance score: {str(e)}")
        return 0.0


def extract_time_series_data(videos: List[Dict[str, Any]], metric: str) -> List[Tuple[datetime, float]]:
    """
    Extract time series data for a specific metric.
    
    Args:
        videos (List[Dict[str, Any]]): Video data
        metric (str): Metric to extract
        
    Returns:
        List[Tuple[datetime, float]]: Time series data
    """
    time_series = []
    
    for video in videos:
        published_at = video.get("published_at")
        if published_at:
            try:
                pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                value = video.get(metric, 0)
                time_series.append((pub_date, float(value)))
            except:
                continue
    
    # Sort by date
    time_series.sort(key=lambda x: x[0])
    return time_series


def calculate_moving_average(data: List[float], window_size: int) -> List[float]:
    """
    Calculate moving average for a data series.
    
    Args:
        data (List[float]): Data series
        window_size (int): Window size for moving average
        
    Returns:
        List[float]: Moving averages
    """
    if len(data) < window_size:
        return data
    
    moving_averages = []
    for i in range(window_size - 1, len(data)):
        window = data[i - window_size + 1:i + 1]
        moving_averages.append(sum(window) / window_size)
    
    return moving_averages


def detect_outliers(data: List[float], method: str = "iqr") -> List[int]:
    """
    Detect outliers in data using specified method.
    
    Args:
        data (List[float]): Data to analyze
        method (str): Method to use ("iqr" or "zscore")
        
    Returns:
        List[int]: Indices of outliers
    """
    if len(data) < 4:
        return []
    
    outlier_indices = []
    
    if method == "iqr":
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        for i, value in enumerate(data):
            if value < lower_bound or value > upper_bound:
                outlier_indices.append(i)
    
    elif method == "zscore":
        mean = np.mean(data)
        std = np.std(data)
        
        for i, value in enumerate(data):
            z_score = abs((value - mean) / std) if std > 0 else 0
            if z_score > 2.5:  # 2.5 standard deviations
                outlier_indices.append(i)
    
    return outlier_indices


def calculate_correlation_matrix(videos: List[Dict[str, Any]], metrics: List[str]) -> Dict[str, Dict[str, float]]:
    """
    Calculate correlation matrix between different metrics.
    
    Args:
        videos (List[Dict[str, Any]]): Video data
        metrics (List[str]): Metrics to correlate
        
    Returns:
        Dict[str, Dict[str, float]]: Correlation matrix
    """
    # Extract metric data
    metric_data = {}
    for metric in metrics:
        metric_data[metric] = [video.get(metric, 0) for video in videos]
    
    # Calculate correlations
    correlation_matrix = {}
    for metric1 in metrics:
        correlation_matrix[metric1] = {}
        for metric2 in metrics:
            if metric1 == metric2:
                correlation_matrix[metric1][metric2] = 1.0
            else:
                try:
                    correlation = np.corrcoef(metric_data[metric1], metric_data[metric2])[0, 1]
                    correlation_matrix[metric1][metric2] = round(correlation, 4) if not np.isnan(correlation) else 0.0
                except:
                    correlation_matrix[metric1][metric2] = 0.0
    
    return correlation_matrix


def analyze_title_patterns(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze title patterns and their impact on performance."""
    try:
        title_analysis = {
            "avg_length": 0,
            "common_words": {},
            "high_performing_patterns": [],
            "length_performance": {}
        }
        
        titles = [video.get("title", "") for video in videos if video.get("title")]
        if not titles:
            return title_analysis
        
        # Average title length
        title_lengths = [len(title) for title in titles]
        title_analysis["avg_length"] = round(np.mean(title_lengths), 1)
        
        # Analyze performance by title length
        length_groups = {
            "short": [v for v in videos if len(v.get("title", "")) < 30],
            "medium": [v for v in videos if 30 <= len(v.get("title", "")) <= 60],
            "long": [v for v in videos if len(v.get("title", "")) > 60]
        }
        
        for group_name, group_videos in length_groups.items():
            if group_videos:
                avg_views = np.mean([v.get("views", 0) for v in group_videos])
                avg_engagement = np.mean([v.get("engagement_rate", 0) for v in group_videos])
                
                title_analysis["length_performance"][group_name] = {
                    "avg_views": round(avg_views, 2),
                    "avg_engagement": round(avg_engagement, 4),
                    "video_count": len(group_videos)
                }
        
        # Common words in high-performing videos
        high_performing_videos = sorted(videos, key=lambda x: x.get("views", 0), reverse=True)[:10]
        word_frequency = defaultdict(int)
        
        for video in high_performing_videos:
            title = video.get("title", "").lower()
            words = title.split()
            for word in words:
                if len(word) > 3:  # Ignore short words
                    word_frequency[word] += 1
        
        title_analysis["common_words"] = dict(sorted(word_frequency.items(), key=lambda x: x[1], reverse=True)[:10])
        
        return title_analysis
        
    except Exception as e:
        logger.error(f"Error analyzing title patterns: {str(e)}")
        return {}


def analyze_duration_patterns(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze video duration patterns and their impact on performance."""
    try:
        duration_analysis = {
            "avg_duration": 0,
            "duration_performance": {},
            "optimal_duration_range": {},
            "retention_by_duration": {}
        }
        
        durations = [video.get("duration", 0) for video in videos if video.get("duration", 0) > 0]
        if not durations:
            return duration_analysis
        
        # Average duration
        duration_analysis["avg_duration"] = round(np.mean(durations), 2)
        
        # Group by duration ranges
        duration_groups = {
            "short": [v for v in videos if 0 < v.get("duration", 0) <= 300],  # 0-5 minutes
            "medium": [v for v in videos if 300 < v.get("duration", 0) <= 600],  # 5-10 minutes
            "long": [v for v in videos if 600 < v.get("duration", 0) <= 1200],  # 10-20 minutes
            "very_long": [v for v in videos if v.get("duration", 0) > 1200]  # 20+ minutes
        }
        
        for group_name, group_videos in duration_groups.items():
            if group_videos:
                avg_views = np.mean([v.get("views", 0) for v in group_videos])
                avg_engagement = np.mean([v.get("engagement_rate", 0) for v in group_videos])
                avg_retention = np.mean([v.get("retention_rate", 0) for v in group_videos])
                
                duration_analysis["duration_performance"][group_name] = {
                    "avg_views": round(avg_views, 2),
                    "avg_engagement": round(avg_engagement, 4),
                    "avg_retention": round(avg_retention, 4),
                    "video_count": len(group_videos)
                }
        
        # Find optimal duration range
        best_performing_group = max(
            duration_analysis["duration_performance"].items(),
            key=lambda x: x[1]["avg_views"] * x[1]["avg_engagement"],
            default=("medium", {})
        )
        
        duration_analysis["optimal_duration_range"] = {
            "range": best_performing_group[0],
            "performance": best_performing_group[1]
        }
        
        return duration_analysis
        
    except Exception as e:
        logger.error(f"Error analyzing duration patterns: {str(e)}")
        return {}


def analyze_category_patterns(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze category performance patterns."""
    try:
        category_analysis = {
            "category_performance": {},
            "best_category": {},
            "category_distribution": {}
        }
        
        # Group by category
        category_groups = defaultdict(list)
        for video in videos:
            category = video.get("category", "unknown")
            category_groups[category].append(video)
        
        # Analyze each category
        for category, category_videos in category_groups.items():
            avg_views = np.mean([v.get("views", 0) for v in category_videos])
            avg_engagement = np.mean([v.get("engagement_rate", 0) for v in category_videos])
            total_revenue = sum(
                v.get("ad_revenue", 0) + v.get("sponsorship_revenue", 0) + v.get("affiliate_revenue", 0)
                for v in category_videos
            )
            
            category_analysis["category_performance"][category] = {
                "avg_views": round(avg_views, 2),
                "avg_engagement": round(avg_engagement, 4),
                "total_revenue": round(total_revenue, 2),
                "video_count": len(category_videos),
                "performance_score": round((avg_views / 1000) + (avg_engagement * 100) + (total_revenue / 10), 2)
            }
        
        # Find best performing category
        if category_analysis["category_performance"]:
            best_category = max(
                category_analysis["category_performance"].items(),
                key=lambda x: x[1]["performance_score"]
            )
            category_analysis["best_category"] = {
                "name": best_category[0],
                "metrics": best_category[1]
            }
        
        # Category distribution
        total_videos = len(videos)
        for category, performance in category_analysis["category_performance"].items():
            percentage = (performance["video_count"] / total_videos) * 100
            category_analysis["category_distribution"][category] = round(percentage, 1)
        
        return category_analysis
        
    except Exception as e:
        logger.error(f"Error analyzing category patterns: {str(e)}")
        return {}


def analyze_tag_patterns(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze tag usage patterns and effectiveness."""
    try:
        tag_analysis = {
            "most_used_tags": {},
            "high_performing_tags": {},
            "tag_effectiveness": {},
            "avg_tags_per_video": 0
        }
        
        # Collect all tags
        all_tags = []
        tag_performance = defaultdict(list)
        
        for video in videos:
            tags = video.get("tags", [])
            all_tags.extend(tags)
            
            # Track performance for each tag
            performance_score = calculate_video_performance_score(video)
            for tag in tags:
                tag_performance[tag].append(performance_score)
        
        if not all_tags:
            return tag_analysis
        
        # Average tags per video
        videos_with_tags = [v for v in videos if v.get("tags")]
        if videos_with_tags:
            tag_analysis["avg_tags_per_video"] = round(
                sum(len(v.get("tags", [])) for v in videos_with_tags) / len(videos_with_tags), 1
            )
        
        # Most used tags
        tag_frequency = defaultdict(int)
        for tag in all_tags:
            tag_frequency[tag] += 1
        
        tag_analysis["most_used_tags"] = dict(
            sorted(tag_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
        )
        
        # High performing tags
        for tag, scores in tag_performance.items():
            if len(scores) >= 2:  # Only consider tags used multiple times
                avg_score = np.mean(scores)
                tag_analysis["tag_effectiveness"][tag] = {
                    "avg_performance": round(avg_score, 2),
                    "usage_count": len(scores)
                }
        
        # Sort by performance
        if tag_analysis["tag_effectiveness"]:
            sorted_tags = sorted(
                tag_analysis["tag_effectiveness"].items(),
                key=lambda x: x[1]["avg_performance"],
                reverse=True
            )
            tag_analysis["high_performing_tags"] = dict(sorted_tags[:10])
        
        return tag_analysis
        
    except Exception as e:
        logger.error(f"Error analyzing tag patterns: {str(e)}")
        return {}


def analyze_posting_time_patterns(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze posting time patterns and their impact on performance."""
    try:
        posting_analysis = {
            "hourly_performance": {},
            "daily_performance": {},
            "best_posting_times": {},
            "posting_frequency": {}
        }
        
        # Group by posting time
        hourly_groups = defaultdict(list)
        daily_groups = defaultdict(list)
        
        for video in videos:
            published_at = video.get("published_at")
            if published_at:
                try:
                    pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    hour = pub_date.hour
                    day = pub_date.strftime("%A")
                    
                    hourly_groups[hour].append(video)
                    daily_groups[day].append(video)
                except:
                    continue
        
        # Analyze hourly performance
        for hour, hour_videos in hourly_groups.items():
            avg_views = np.mean([v.get("views", 0) for v in hour_videos])
            avg_engagement = np.mean([v.get("engagement_rate", 0) for v in hour_videos])
            
            posting_analysis["hourly_performance"][hour] = {
                "avg_views": round(avg_views, 2),
                "avg_engagement": round(avg_engagement, 4),
                "video_count": len(hour_videos)
            }
        
        # Analyze daily performance
        for day, day_videos in daily_groups.items():
            avg_views = np.mean([v.get("views", 0) for v in day_videos])
            avg_engagement = np.mean([v.get("engagement_rate", 0) for v in day_videos])
            
            posting_analysis["daily_performance"][day] = {
                "avg_views": round(avg_views, 2),
                "avg_engagement": round(avg_engagement, 4),
                "video_count": len(day_videos)
            }
        
        # Find best posting times
        if posting_analysis["hourly_performance"]:
            best_hour = max(
                posting_analysis["hourly_performance"].items(),
                key=lambda x: x[1]["avg_views"] * x[1]["avg_engagement"]
            )
            posting_analysis["best_posting_times"]["hour"] = {
                "time": f"{best_hour[0]:02d}:00",
                "performance": best_hour[1]
            }
        
        if posting_analysis["daily_performance"]:
            best_day = max(
                posting_analysis["daily_performance"].items(),
                key=lambda x: x[1]["avg_views"] * x[1]["avg_engagement"]
            )
            posting_analysis["best_posting_times"]["day"] = {
                "day": best_day[0],
                "performance": best_day[1]
            }
        
        return posting_analysis
        
    except Exception as e:
        logger.error(f"Error analyzing posting time patterns: {str(e)}")
        return {}


def calculate_engagement_velocity(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate how quickly videos gain engagement after posting."""
    try:
        velocity_analysis = {
            "avg_velocity": 0,
            "velocity_by_category": {},
            "high_velocity_videos": [],
            "velocity_trends": {}
        }
        
        velocities = []
        category_velocities = defaultdict(list)
        
        for video in videos:
            published_at = video.get("published_at")
            if published_at:
                try:
                    pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    days_since_publish = (datetime.now(pub_date.tzinfo) - pub_date).days
                    
                    if days_since_publish > 0:
                        # Calculate engagement velocity (engagement per day)
                        total_engagement = (video.get("likes", 0) + 
                                          video.get("comments", 0) + 
                                          video.get("shares", 0))
                        velocity = total_engagement / days_since_publish
                        
                        velocities.append(velocity)
                        category = video.get("category", "unknown")
                        category_velocities[category].append(velocity)
                        
                        # Track high velocity videos
                        if velocity > 100:  # More than 100 engagements per day
                            velocity_analysis["high_velocity_videos"].append({
                                "title": video.get("title", ""),
                                "velocity": round(velocity, 2),
                                "days_old": days_since_publish
                            })
                except:
                    continue
        
        if velocities:
            velocity_analysis["avg_velocity"] = round(np.mean(velocities), 2)
            
            # Velocity by category
            for category, cat_velocities in category_velocities.items():
                velocity_analysis["velocity_by_category"][category] = {
                    "avg_velocity": round(np.mean(cat_velocities), 2),
                    "video_count": len(cat_velocities)
                }
            
            # Sort high velocity videos
            velocity_analysis["high_velocity_videos"].sort(
                key=lambda x: x["velocity"], reverse=True
            )
            velocity_analysis["high_velocity_videos"] = velocity_analysis["high_velocity_videos"][:10]
        
        return velocity_analysis
        
    except Exception as e:
        logger.error(f"Error calculating engagement velocity: {str(e)}")
        return {}


def analyze_content_lifecycle(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze content lifecycle and longevity patterns.
    
    Args:
        videos: List of normalized video data
        
    Returns:
        Content lifecycle analysis
    """
    try:
        # Simulate lifecycle stages (in production, this would use actual view history data)
        lifecycle_stages = [
            {"stage": "Launch", "duration_days": 7, "view_percentage": 0.6, "description": "Initial surge of views"},
            {"stage": "Growth", "duration_days": 30, "view_percentage": 0.3, "description": "Sustained growth period"},
            {"stage": "Mature", "duration_days": 90, "view_percentage": 0.1, "description": "Long-tail performance"}
        ]
        
        # Calculate average performance metrics
        avg_views = mean([v.get('views', 0) for v in videos]) if videos else 0
        peak_performance_day = 3  # Typically day 3 for most content
        
        # Calculate longevity score based on engagement patterns
        longevity_scores = []
        for video in videos:
            engagement = video.get('engagement_score', 0)
            views = video.get('views', 0)
            # Higher engagement and views suggest better longevity
            longevity_score = min((engagement * 1000 + views / 1000) / 2, 100)
            longevity_scores.append(longevity_score)
        
        avg_longevity_score = mean(longevity_scores) if longevity_scores else 0
        
        return {
            "lifecycle_stages": lifecycle_stages,
            "peak_performance_day": peak_performance_day,
            "longevity_score": round(avg_longevity_score, 1),
            "avg_views": int(avg_views),
            "content_decay_rate": 0.15,  # 15% decay per month (typical)
            "evergreen_content_percentage": len([v for v in videos if v.get('engagement_score', 0) > 0.05]) / len(videos) * 100 if videos else 0
        }
        
    except Exception as e:
        logger.error(f"Error analyzing content lifecycle: {str(e)}")
        raise


def calculate_audience_retention_metrics(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate detailed audience retention metrics.
    
    Args:
        videos: List of normalized video data
        
    Returns:
        Audience retention analysis
    """
    try:
        if not videos:
            return {"error": "No video data available"}
        
        # Simulate retention curve (in production, this would come from YouTube Analytics)
        retention_curve = []
        for i in range(0, 301, 30):  # 5-minute video in 30-second intervals
            # Typical retention curve: starts at 100%, drops quickly, then gradually
            if i == 0:
                retention = 100
            elif i <= 60:
                retention = 100 - (i * 0.5)  # 0.5% drop per 30 seconds initially
            else:
                retention = max(70 - ((i - 60) * 0.2), 20)  # Slower drop, minimum 20%
            
            retention_curve.append({
                "timestamp": i,
                "retention_percentage": round(retention, 1)
            })
        
        # Calculate average retention rate
        avg_retention_rate = mean([point["retention_percentage"] for point in retention_curve]) / 100
        
        # Identify drop-off points (significant retention drops)
        drop_off_points = []
        for i in range(1, len(retention_curve)):
            current = retention_curve[i]["retention_percentage"]
            previous = retention_curve[i-1]["retention_percentage"]
            drop = previous - current
            
            if drop > 5:  # More than 5% drop
                drop_off_points.append({
                    "timestamp": retention_curve[i]["timestamp"],
                    "drop_percentage": round(drop, 1),
                    "reason": "Content transition" if i < 3 else "Engagement drop"
                })
        
        # Identify engagement hotspots (where retention improves)
        engagement_hotspots = []
        for i in range(1, len(retention_curve)):
            current = retention_curve[i]["retention_percentage"]
            previous = retention_curve[i-1]["retention_percentage"]
            
            if current > previous:  # Retention improved
                engagement_hotspots.append({
                    "timestamp": retention_curve[i]["timestamp"],
                    "engagement_spike": round(current / previous, 2)
                })
        
        # Calculate average watch time
        total_duration = mean([v.get('duration', 0) for v in videos])
        avg_watch_time = total_duration * avg_retention_rate
        
        return {
            "avg_retention_rate": round(avg_retention_rate, 3),
            "avg_watch_time": round(avg_watch_time, 0),
            "retention_curve": retention_curve,
            "drop_off_points": drop_off_points,
            "engagement_hotspots": engagement_hotspots,
            "total_watch_time": sum(v.get('views', 0) * avg_watch_time for v in videos)
        }
        
    except Exception as e:
        logger.error(f"Error calculating retention metrics: {str(e)}")
        raise


def generate_performance_benchmarks(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate performance benchmarks based on historical data."""
    try:
        benchmarks = {
            "views": {},
            "engagement_rate": {},
            "retention_rate": {},
            "revenue": {},
            "performance_tiers": {}
        }
        
        # Extract metrics
        views = [v.get("views", 0) for v in videos if v.get("views", 0) > 0]
        engagement_rates = [v.get("engagement_rate", 0) for v in videos if v.get("engagement_rate", 0) > 0]
        retention_rates = [v.get("retention_rate", 0) for v in videos if v.get("retention_rate", 0) > 0]
        
        revenues = []
        for video in videos:
            total_revenue = (video.get("ad_revenue", 0) + 
                           video.get("sponsorship_revenue", 0) + 
                           video.get("affiliate_revenue", 0))
            if total_revenue > 0:
                revenues.append(total_revenue)
        
        # Calculate percentile benchmarks
        metrics = {
            "views": views,
            "engagement_rate": engagement_rates,
            "retention_rate": retention_rates,
            "revenue": revenues
        }
        
        for metric_name, metric_data in metrics.items():
            if metric_data:
                benchmarks[metric_name] = {
                    "min": round(min(metric_data), 4),
                    "p25": round(np.percentile(metric_data, 25), 4),
                    "median": round(np.percentile(metric_data, 50), 4),
                    "p75": round(np.percentile(metric_data, 75), 4),
                    "p90": round(np.percentile(metric_data, 90), 4),
                    "max": round(max(metric_data), 4),
                    "mean": round(np.mean(metric_data), 4)
                }
        
        # Define performance tiers
        if views:
            view_p25 = np.percentile(views, 25)
            view_p75 = np.percentile(views, 75)
            view_p90 = np.percentile(views, 90)
            
            benchmarks["performance_tiers"] = {
                "poor": {"min_views": 0, "max_views": view_p25},
                "average": {"min_views": view_p25, "max_views": view_p75},
                "good": {"min_views": view_p75, "max_views": view_p90},
                "excellent": {"min_views": view_p90, "max_views": float('inf')}
            }
        
        return benchmarks
        
    except Exception as e:
        logger.error(f"Error generating benchmarks: {str(e)}")
        return {}


def calculate_competitive_metrics(channel_data: Dict[str, Any], industry_benchmarks: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate competitive metrics against industry benchmarks.
    
    Args:
        channel_data: Channel performance data
        industry_benchmarks: Industry benchmark data
        
    Returns:
        Competitive analysis metrics
    """
    try:
        videos = channel_data.get("videos", [])
        if not videos:
            return {"error": "No video data available"}
        
        # Calculate channel metrics
        avg_views = mean([v.get("views", 0) for v in videos])
        avg_engagement = mean([v.get("engagement_score", 0) for v in videos])
        avg_revenue = mean([v.get("revenue_total", 0) for v in videos])
        
        # Compare against benchmarks
        views_vs_benchmark = (avg_views / industry_benchmarks.get('avg_views', 1)) * 100
        engagement_vs_benchmark = (avg_engagement / industry_benchmarks.get('avg_engagement', 0.01)) * 100
        revenue_vs_benchmark = (avg_revenue / industry_benchmarks.get('revenue_per_video', 1)) * 100
        
        # Calculate overall competitive score
        competitive_score = mean([views_vs_benchmark, engagement_vs_benchmark, revenue_vs_benchmark])
        
        # Identify strengths and improvement areas
        strengths = []
        improvement_areas = []
        
        if views_vs_benchmark > 100:
            strengths.append("Views performance above industry average")
        else:
            improvement_areas.append("Views performance below industry average")
        
        if engagement_vs_benchmark > 100:
            strengths.append("Engagement rate above industry average")
        else:
            improvement_areas.append("Engagement rate below industry average")
        
        if revenue_vs_benchmark > 100:
            strengths.append("Revenue performance above industry average")
        else:
            improvement_areas.append("Revenue performance below industry average")
        
        return {
            "performance_vs_industry": {
                "views": round(views_vs_benchmark, 1),
                "engagement": round(engagement_vs_benchmark, 1),
                "revenue": round(revenue_vs_benchmark, 1)
            },
            "competitive_score": round(competitive_score, 1),
            "strengths": strengths,
            "improvement_areas": improvement_areas,
            "benchmarks": {
                "views": {"current": int(avg_views), "industry_avg": industry_benchmarks.get('avg_views', 0), "gap": round(views_vs_benchmark - 100, 1)},
                "engagement": {"current": round(avg_engagement, 4), "industry_avg": industry_benchmarks.get('avg_engagement', 0), "gap": round(engagement_vs_benchmark - 100, 1)},
                "revenue": {"current": round(avg_revenue, 2), "industry_avg": industry_benchmarks.get('revenue_per_video', 0), "gap": round(revenue_vs_benchmark - 100, 1)}
            }
        }
        
    except Exception as e:
        logger.error(f"Error calculating competitive metrics: {str(e)}")
        raise


def export_analytics_data(data: Dict[str, Any], format: str) -> str:
    """
    Export analytics data in specified format.
    
    Args:
        data: Analytics data to export
        format: Export format (json, csv, xlsx)
        
    Returns:
        Exported data as string
    """
    try:
        if format.lower() == "json":
            return json.dumps(data, indent=2, default=str)
        
        elif format.lower() == "csv":
            # Convert nested data to flat structure for CSV
            flattened_data = flatten_dict(data)
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            writer.writerow(flattened_data.keys())
            
            # Write data
            writer.writerow(flattened_data.values())
            
            return output.getvalue()
        
        else:
            # Default to plain text
            return str(data)
        
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")
        return f"Error exporting data: {str(e)}"


# Utility functions for data validation and cleaning
def validate_video_data(video: Dict[str, Any]) -> bool:
    """Validate video data structure and required fields."""
    required_fields = ["title", "views"]
    
    for field in required_fields:
        if field not in video or video[field] is None:
            return False
    
    # Validate data types
    numeric_fields = ["views", "likes", "comments", "shares", "duration"]
    for field in numeric_fields:
        if field in video and not isinstance(video[field], (int, float)):
            try:
                video[field] = float(video[field])
            except (ValueError, TypeError):
                video[field] = 0
    
    return True


def clean_video_data(videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Clean and validate video data."""
    cleaned_videos = []
    
    for video in videos:
        if validate_video_data(video):
            cleaned_video = normalize_video_data([video])[0]
            cleaned_videos.append(cleaned_video)
    
    return cleaned_videos


# Export all utility functions
__all__ = [
    'normalize_video_data',
    'calculate_video_performance_score',
    'extract_time_series_data',
    'calculate_moving_average',
    'detect_outliers',
    'calculate_correlation_matrix',
    # 'identify_content_patterns', # Removed as AdvancedAnalyticsEngine provides more comprehensive content analysis
    'analyze_title_patterns',
    'analyze_duration_patterns',
    'analyze_category_patterns',
    'analyze_tag_patterns',
    'analyze_posting_time_patterns',
    'calculate_engagement_velocity',
    'analyze_content_lifecycle',
    'calculate_audience_retention_metrics',
    'generate_performance_benchmarks',
    'calculate_competitive_metrics',
    'export_analytics_data',
    'validate_video_data',
    'clean_video_data'
]

def generate_recommendations(videos: List[Dict[str, Any]], channel_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate actionable recommendations based on analysis."""
    try:
        recommendations = []
        
        if not videos:
            return [{"type": "content", "priority": "high", "recommendation": "Start creating content to build analytics data"}]
        
        # Performance-based recommendations
        avg_performance = mean([v.get('performance_score', 0) for v in videos])
        if avg_performance < 50:
            recommendations.append({
                "type": "performance",
                "priority": "high",
                "recommendation": "Focus on improving content quality and engagement",
                "impact_score": 9,
                "steps": [
                    "Analyze top-performing videos for patterns",
                    "Improve thumbnail design",
                    "Optimize video titles for SEO",
                    "Increase audience interaction"
                ]
            })
        
        # Engagement recommendations
        avg_engagement = mean([v.get('engagement_score', 0) for v in videos])
        if avg_engagement < 0.03:  # Less than 3% engagement
            recommendations.append({
                "type": "engagement",
                "priority": "high",
                "recommendation": "Implement strategies to boost audience engagement",
                "impact_score": 8,
                "steps": [
                    "Add call-to-actions in videos",
                    "Respond to comments promptly",
                    "Create interactive content",
                    "Use engaging thumbnails and titles"
                ]
            })
        
        # Revenue optimization
        total_revenue = sum(v.get('revenue_total', 0) for v in videos)
        if total_revenue < len(videos) * 100:  # Less than $100 per video average
            recommendations.append({
                "type": "monetization",
                "priority": "medium",
                "recommendation": "Explore additional revenue streams",
                "impact_score": 7,
                "steps": [
                    "Seek sponsorship opportunities",
                    "Add affiliate marketing",
                    "Create premium content",
                    "Optimize ad placement"
                ]
            })
        
        # Content consistency
        if len(videos) > 0:
            # Check upload frequency
            sorted_videos = sorted(videos, key=lambda x: x.get('published_at', ''))
            if len(sorted_videos) >= 2:
                # Calculate average days between uploads
                date_diffs = []
                for i in range(1, len(sorted_videos)):
                    try:
                        date1 = datetime.fromisoformat(sorted_videos[i-1].get('published_at', '').replace('Z', '+00:00'))
                        date2 = datetime.fromisoformat(sorted_videos[i].get('published_at', '').replace('Z', '+00:00'))
                        diff = (date2 - date1).days
                        date_diffs.append(diff)
                    except:
                        continue
                
                if date_diffs:
                    avg_gap = mean(date_diffs)
                    if avg_gap > 14:  # More than 2 weeks between uploads
                        recommendations.append({
                            "type": "consistency",
                            "priority": "medium",
                            "recommendation": "Maintain more consistent upload schedule",
                            "impact_score": 6,
                            "steps": [
                                "Create content calendar",
                                "Batch produce content",
                                "Set realistic upload goals",
                                "Use scheduling tools"
                            ]
                        })
        
        # Category diversification
        categories = set(v.get('category', 'unknown') for v in videos)
        if len(categories) == 1 and len(videos) > 5:
            recommendations.append({
                "type": "content_strategy",
                "priority": "low",
                "recommendation": "Consider diversifying content categories",
                "impact_score": 5,
                "steps": [
                    "Research related topics",
                    "Test new content types",
                    "Analyze audience interests",
                    "Gradually introduce variety"
                ]
            })
        
        # Sort by priority and impact
        priority_order = {"high": 3, "medium": 2, "low": 1}
        recommendations.sort(key=lambda x: (priority_order.get(x['priority'], 0), x.get('impact_score', 0)), reverse=True)
        
        return recommendations[:10]  # Return top 10 recommendations
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        return []

def calculate_historical_growth_rates(videos: List[Dict[str, Any]]) -> List[float]:
    """Calculate historical growth rates from video performance."""
    try:
        if len(videos) < 2:
            return []
        
        growth_rates = []
        for i in range(1, len(videos)):
            current_views = videos[i].get('views', 0)
            previous_views = videos[i-1].get('views', 0)
            
            if previous_views > 0:
                growth_rate = (current_views - previous_views) / previous_views
                growth_rates.append(growth_rate)
        
        return growth_rates
        
    except Exception as e:
        logger.error(f"Error calculating growth rates: {str(e)}")
        return []

def generate_simulated_demographics() -> List[Dict[str, Any]]:
    """Generate simulated demographic data (placeholder for real analytics)."""
    return [
        {"age_group": "13-17", "percentage": 15},
        {"age_group": "18-24", "percentage": 35},
        {"age_group": "25-34", "percentage": 30},
        {"age_group": "35-44", "percentage": 15},
        {"age_group": "45-54", "percentage": 4},
        {"age_group": "55+", "percentage": 1}
    ]

def analyze_engagement_patterns(videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Analyze engagement patterns throughout the day."""
    # Simulated engagement patterns (in production, use real data)
    return [
        {"hour": 6, "engagement_rate": 0.025},
        {"hour": 8, "engagement_rate": 0.035},
        {"hour": 12, "engagement_rate": 0.045},
        {"hour": 14, "engagement_rate": 0.065},
        {"hour": 16, "engagement_rate": 0.055},
        {"hour": 18, "engagement_rate": 0.070},
        {"hour": 20, "engagement_rate": 0.058},
        {"hour": 22, "engagement_rate": 0.040}
    ]

def calculate_subscriber_conversion_rate(videos: List[Dict[str, Any]], channel_data: Dict[str, Any]) -> float:
    """Calculate subscriber conversion rate."""
    try:
        total_views = sum(v.get('views', 0) for v in videos)
        subscriber_count = channel_data.get('subscriber_count', 0)
        
        if total_views > 0:
            # Estimate conversion rate (this would be more accurate with real data)
            return round(subscriber_count / total_views * 100, 3)
        return 0
        
    except Exception as e:
        logger.error(f"Error calculating conversion rate: {str(e)}")
        return 0

def calculate_score_breakdown(videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Calculate performance score breakdown by category."""
    try:
        categories = ["Content Quality", "Engagement", "Revenue", "Consistency", "SEO"]
        breakdown = []
        
        for category in categories:
            if category == "Content Quality":
                # Based on views and performance scores
                scores = [v.get('performance_score', 0) for v in videos]
                avg_score = mean(scores) if scores else 0
            elif category == "Engagement":
                # Based on engagement rates
                engagement_scores = [v.get('engagement_score', 0) * 1000 for v in videos]  # Scale up
                avg_score = min(mean(engagement_scores) if engagement_scores else 0, 100)
            elif category == "Revenue":
                # Based on revenue performance
                revenue_scores = [min(v.get('revenue_total', 0) / 10, 100) for v in videos]
                avg_score = mean(revenue_scores) if revenue_scores else 0
            elif category == "Consistency":
                # Based on performance consistency
                scores = [v.get('performance_score', 0) for v in videos]
                if len(scores) > 1:
                    consistency = 100 - min(stdev(scores), 50)  # Cap at 50 for very inconsistent
                else:
                    consistency = 50  # Neutral for single video
                avg_score = consistency
            else:  # SEO
                # Simulated SEO score based on title length and engagement
                seo_scores = []
                for video in videos:
                    title_length = len(video.get('title', ''))
                    engagement = video.get('engagement_score', 0)
                    # Good title length (40-60 chars) + engagement
                    title_score = 100 if 40 <= title_length <= 60 else max(50, 100 - abs(title_length - 50))
                    engagement_score = min(engagement * 1000, 100)
                    seo_score = (title_score + engagement_score) / 2
                    seo_scores.append(seo_score)
                avg_score = mean(seo_scores) if seo_scores else 0
            
            breakdown.append({
                "category": category,
                "score": round(avg_score, 1)
            })
        
        return breakdown
        
    except Exception as e:
        logger.error(f"Error calculating score breakdown: {str(e)}")
        return []

def create_content_performance_matrix(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create a performance matrix for content analysis."""
    try:
        if not videos:
            return {}
        
        # Performance vs Engagement matrix
        performance_scores = [v.get('performance_score', 0) for v in videos]
        engagement_scores = [v.get('engagement_score', 0) * 1000 for v in videos]  # Scale up
        
        # Categorize videos into quadrants
        avg_performance = mean(performance_scores)
        avg_engagement = mean(engagement_scores)
        
        quadrants = {
            "high_performance_high_engagement": [],
            "high_performance_low_engagement": [],
            "low_performance_high_engagement": [],
            "low_performance_low_engagement": []
        }
        
        for i, video in enumerate(videos):
            perf = performance_scores[i]
            eng = engagement_scores[i]
            
            if perf >= avg_performance and eng >= avg_engagement:
                quadrants["high_performance_high_engagement"].append(video.get('title', f'Video {i+1}'))
            elif perf >= avg_performance and eng < avg_engagement:
                quadrants["high_performance_low_engagement"].append(video.get('title', f'Video {i+1}'))
            elif perf < avg_performance and eng >= avg_engagement:
                quadrants["low_performance_high_engagement"].append(video.get('title', f'Video {i+1}'))
            else:
                quadrants["low_performance_low_engagement"].append(video.get('title', f'Video {i+1}'))
        
        return {
            "quadrants": quadrants,
            "avg_performance": round(avg_performance, 1),
            "avg_engagement": round(avg_engagement / 1000, 4),  # Scale back down
            "total_videos": len(videos)
        }
        
    except Exception as e:
        logger.error(f"Error creating performance matrix: {str(e)}")
        return {}

def identify_top_performing_content(videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Identify top performing content."""
    try:
        if not videos:
            return []
        
        # Sort by performance score
        sorted_videos = sorted(videos, key=lambda x: x.get('performance_score', 0), reverse=True)
        
        top_content = []
        for video in sorted_videos[:5]:  # Top 5
            top_content.append({
                "title": video.get('title', 'Untitled'),
                "performance_score": round(video.get('performance_score', 0), 1),
                "views": video.get('views', 0),
                "engagement_rate": round(video.get('engagement_score', 0), 4),
                "revenue": video.get('revenue_total', 0),
                "category": video.get('category', 'unknown')
            })
        
        return top_content
        
    except Exception as e:
        logger.error(f"Error identifying top content: {str(e)}")
        return []

def create_performance_timeline(videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create a timeline of performance metrics."""
    try:
        if not videos:
            return []
        
        # Sort by publication date
        sorted_videos = sorted(videos, key=lambda x: x.get('published_at', ''))

        timeline = []
        for video in sorted_videos:
            try:
                pub_date = video.get('published_at', '')
                if pub_date:
                    # Parse date (handle different formats)
                    if 'T' in pub_date:
                        date_obj = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                    else:
                        date_obj = datetime.strptime(pub_date, '%Y-%m-%d')
                    
                    timeline.append({
                        "date": date_obj.strftime('%Y-%m-%d'),
                        "title": video.get('title', 'Untitled'),
                        "performance_score": round(video.get('performance_score', 0), 1),
                        "views": video.get('views', 0),
                        "engagement_rate": round(video.get('engagement_score', 0), 4),
                        "revenue": video.get('revenue_total', 0)
                    })
            except Exception as date_error:
                logger.warning(f"Error parsing date for video: {date_error}")
                continue
        
        return timeline
        
    except Exception as e:
        logger.error(f"Error creating performance timeline: {str(e)}")
        return []

def predict_trends(videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Predict future trends based on historical data."""
    try:
        if len(videos) < 3:
            return []
        
        predictions = []
        metrics = ['views', 'engagement_score', 'revenue_total']
        
        for metric in metrics:
            values = [v.get(metric, 0) for v in videos[-5:]]  # Last 5 videos
            
            if len(values) >= 3:
                # Simple trend prediction using linear regression concept
                x = list(range(len(values)))
                y = values
                
                # Calculate slope (trend direction)
                n = len(values)
                sum_x = sum(x)
                sum_y = sum(y)
                sum_xy = sum(x[i] * y[i] for i in range(n))
                sum_x2 = sum(xi * xi for xi in x)
                
                if n * sum_x2 - sum_x * sum_x != 0:
                    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                    
                    # Predict next value
                    next_value = y[-1] + slope
                    
                    # Determine trend direction and confidence
                    if slope > 0.1:
                        direction = "increasing"
                        confidence = min(70 + abs(slope) * 10, 90)
                    elif slope < -0.1:
                        direction = "decreasing"
                        confidence = min(70 + abs(slope) * 10, 90)
                    else:
                        direction = "stable"
                        confidence = 60
                    
                    predictions.append({
                        "metric": metric.replace('_', ' ').title(),
                        "current_value": round(y[-1], 2),
                        "predicted_value": round(max(0, next_value), 2),
                        "trend_direction": direction,
                        "confidence": round(confidence, 0),
                        "change_rate": round(slope, 3)
                    })
        
        return predictions
        
    except Exception as e:
        logger.error(f"Error predicting trends: {str(e)}")
        return []

def predict_performance_changes(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Predict performance changes for different content strategies."""
    try:
        if not videos:
            return {}
        
        current_avg_performance = mean([v.get('performance_score', 0) for v in videos])
        
        # Simulate different strategy impacts
        strategies = {
            "improve_thumbnails": {
                "impact": 15,
                "confidence": 80,
                "description": "Optimize thumbnail design and colors"
            },
            "better_titles": {
                "impact": 12,
                "confidence": 85,
                "description": "Use more engaging and SEO-friendly titles"
            },
            "consistent_posting": {
                "impact": 20,
                "confidence": 75,
                "description": "Maintain regular upload schedule"
            },
            "audience_engagement": {
                "impact": 18,
                "confidence": 70,
                "description": "Increase interaction with audience"
            },
            "content_quality": {
                "impact": 25,
                "confidence": 90,
                "description": "Improve overall content production value"
            }
        }
        
        predictions = []
        for strategy, data in strategies.items():
            predicted_score = min(current_avg_performance + data["impact"], 100)
            predictions.append({
                "strategy": strategy.replace('_', ' ').title(),
                "current_score": round(current_avg_performance, 1),
                "predicted_score": round(predicted_score, 1),
                "improvement": data["impact"],
                "confidence": data["confidence"],
                "description": data["description"]
            })
        
        # Sort by potential improvement
        predictions.sort(key=lambda x: x["improvement"], reverse=True)
        
        return {
            "predictions": predictions,
            "current_baseline": round(current_avg_performance, 1),
            "max_potential": round(min(current_avg_performance + 50, 100), 1)
        }
        
    except Exception as e:
        logger.error(f"Error predicting performance changes: {str(e)}")
        return {}

def forecast_revenue(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Forecast revenue based on historical performance."""
    try:
        if not videos:
            return {}
        
        # Calculate current revenue metrics
        total_revenue = sum(v.get('revenue_total', 0) for v in videos)
        avg_revenue_per_video = total_revenue / len(videos) if videos else 0
        
        # Revenue growth rate
        if len(videos) >= 2:
            recent_videos = videos[-3:] if len(videos) >= 3 else videos[-2:]
            older_videos = videos[:-3] if len(videos) >= 6 else videos[:-2]
            
            recent_avg = mean([v.get('revenue_total', 0) for v in recent_videos])
            older_avg = mean([v.get('revenue_total', 0) for v in older_videos]) if older_videos else recent_avg
            
            if older_avg > 0:
                growth_rate = (recent_avg - older_avg) / older_avg
            else:
                growth_rate = 0
        else:
            growth_rate = 0.1  # Assume 10% growth for new channels
        
        # Forecast next 6 months
        monthly_forecasts = []
        current_monthly_revenue = avg_revenue_per_video * 4  # Assume 4 videos per month
        
        for month in range(1, 7):
            projected_revenue = current_monthly_revenue * (1 + growth_rate) ** month
            confidence = max(90 - month * 10, 50)  # Decreasing confidence over time
            
            monthly_forecasts.append({
                "month": month,
                "projected_revenue": round(projected_revenue, 2),
                "confidence": confidence
            })
        
        # Revenue stream breakdown forecast
        ad_revenue_ratio = sum(v.get('ad_revenue', 0) for v in videos) / total_revenue if total_revenue > 0 else 0.4
        sponsorship_ratio = sum(v.get('sponsorship_revenue', 0) for v in videos) / total_revenue if total_revenue > 0 else 0.4
        affiliate_ratio = sum(v.get('affiliate_revenue', 0) for v in videos) / total_revenue if total_revenue > 0 else 0.2
        
        return {
            "monthly_forecasts": monthly_forecasts,
            "current_metrics": {
                "total_revenue": round(total_revenue, 2),
                "avg_revenue_per_video": round(avg_revenue_per_video, 2),
                "growth_rate": round(growth_rate * 100, 1)
            },
            "revenue_stream_forecast": {
                "ad_revenue_percentage": round(ad_revenue_ratio * 100, 1),
                "sponsorship_percentage": round(sponsorship_ratio * 100, 1),
                "affiliate_percentage": round(affiliate_ratio * 100, 1)
            },
            "annual_projection": round(sum(f["projected_revenue"] for f in monthly_forecasts) * 2, 2)  # Extrapolate to full year
        }
        
    except Exception as e:
        logger.error(f"Error forecasting revenue: {str(e)}")
        return {}

def calculate_prediction_confidence(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate confidence metrics for predictions."""
    try:
        data_points = len(videos)
        
        # Base confidence on amount of data
        if data_points >= 20:
            base_confidence = 85
        elif data_points >= 10:
            base_confidence = 75
        elif data_points >= 5:
            base_confidence = 65
        else:
            base_confidence = 50
        
        # Adjust for data consistency
        if videos:
            performance_scores = [v.get('performance_score', 0) for v in videos]
            if len(performance_scores) > 1:
                consistency = 100 - min(stdev(performance_scores), 50)
                confidence_adjustment = (consistency - 50) / 50 * 10  # ±10 points based on consistency
            else:
                confidence_adjustment = 0
        else:
            confidence_adjustment = -20
        
        final_confidence = max(30, min(95, base_confidence + confidence_adjustment))
        
        return {
            "overall_confidence": round(final_confidence, 1),
            "data_points": data_points,
            "consistency_score": round(50 + confidence_adjustment * 5, 1),
            "confidence_factors": {
                "data_volume": "High" if data_points >= 20 else "Medium" if data_points >= 10 else "Low",
                "data_consistency": "High" if confidence_adjustment > 5 else "Medium" if confidence_adjustment > -5 else "Low",
                "prediction_reliability": "High" if final_confidence > 80 else "Medium" if final_confidence > 60 else "Low"
            }
        }
        
    except Exception as e:
        logger.error(f"Error calculating prediction confidence: {str(e)}")
        return {"overall_confidence": 50, "data_points": 0}

def generate_content_recommendations(videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate content-specific recommendations."""
    try:
        recommendations = []
        
        if not videos:
            return [{
                "type": "content_creation",
                "priority": "high",
                "action": "Start creating content consistently",
                "impact_score": 10,
                "steps": ["Plan content calendar", "Create first video", "Establish upload schedule"]
            }]
        
        # Analyze top performing content
        top_videos = sorted(videos, key=lambda x: x.get('performance_score', 0), reverse=True)[:3]
        
        if top_videos:
            # Find common characteristics
            top_categories = [v.get('category', 'unknown') for v in top_videos]
            most_common_category = max(set(top_categories), key=top_categories.count)
            
            recommendations.append({
                "type": "content_focus",
                "priority": "high",
                "action": f"Create more content in the '{most_common_category}' category",
                "impact_score": 8,
                "steps": [
                    f"Research trending topics in {most_common_category}",
                    "Analyze successful video formats",
                    "Plan 3-5 videos in this category"
                ]
            })
        
        # Duration recommendations
        duration_performance = {}
        for video in videos:
            duration = video.get('duration', 0)
            performance = video.get('performance_score', 0)
            
            if duration <= 300:  # 5 minutes
                duration_key = "short"
            elif duration <= 900:  # 15 minutes
                duration_key = "medium"
            else:
                duration_key = "long"
            
            if duration_key not in duration_performance:
                duration_performance[duration_key] = []
            duration_performance[duration_key].append(performance)
        
        # Find best performing duration
        best_duration = None
        best_performance = 0
        for duration_type, performances in duration_performance.items():
            avg_performance = mean(performances)
            if avg_performance > best_performance:
                best_performance = avg_performance
                best_duration = duration_type
        
        if best_duration:
            duration_map = {
                "short": "5-10 minutes",
                "medium": "10-15 minutes", 
                "long": "15+ minutes"
            }
            recommendations.append({
                "type": "video_length",
                "priority": "medium",
                "action": f"Focus on {duration_map[best_duration]} video length",
                "impact_score": 6,
                "steps": [
                    f"Plan content for {duration_map[best_duration]} format",
                    "Structure videos with clear segments",
                    "Test different lengths within this range"
                ]
            })
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generating content recommendations: {str(e)}")
        return []

def analyze_posting_patterns(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze optimal posting patterns."""
    try:
        if not videos:
            return {}
        
        # Simulate posting time analysis (in production, use real data)
        posting_analysis = {
            "best_day": {
                "day": "Tuesday",
                "performance_multiplier": 1.25,
                "reasoning": "Higher engagement on weekdays"
            },
            "best_time": {
                "time": "14:00",
                "performance_multiplier": 1.15,
                "reasoning": "Peak audience activity time"
            },
            "frequency_recommendation": {
                "current_frequency": "irregular",
                "recommended_frequency": "3 times per week",
                "reasoning": "Consistent posting improves algorithm performance"
            },
            "seasonal_trends": [
                {"period": "January", "performance_factor": 0.9},
                {"period": "March", "performance_factor": 1.1},
                {"period": "June", "performance_factor": 1.2},
                {"period": "September", "performance_factor": 1.15},
                {"period": "December", "performance_factor": 0.95}
            ]
        }
        
        return posting_analysis
        
    except Exception as e:
        logger.error(f"Error analyzing posting patterns: {str(e)}")
        return {}

def generate_seo_recommendations(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate SEO optimization recommendations."""
    try:
        if not videos:
            return {}
        
        # Analyze current SEO performance
 title_lengths = [len(v.get('title', '')) for v in videos]
        avg_title_length = mean(title_lengths) if title_lengths else 0
        
        seo_recommendations = {
            "title_optimization": {
                "current_avg_length": round(avg_title_length, 0),
                "recommended_length": "50-60 characters",
                "improvement_needed": avg_title_length < 40 or avg_title_length > 70,
                "tips": [
                    "Include target keywords in first 50 characters",
                    "Use compelling action words",
                    "Add numbers or brackets for better CTR",
                    "Avoid clickbait - focus on value proposition"
                ]
            },
            "keyword_strategy": {
                "primary_keywords": "Focus on 1-2 main keywords per video",
                "long_tail_keywords": "Target specific, less competitive phrases",
                "keyword_placement": [
                    "Title (first 50 characters)",
                    "Description (first 125 characters)",
                    "Tags (5-10 relevant tags)",
                    "Video content (spoken keywords)"
                ]
            },
            "description_optimization": {
                "recommended_length": "200+ characters",
                "structure": [
                    "Hook (first 125 characters)",
                    "Detailed explanation",
                    "Call to action",
                    "Links and social media",
                    "Hashtags (3-5 relevant)"
                ]
            },
            "thumbnail_seo": {
                "best_practices": [
                    "Use high contrast colors",
                    "Include readable text (if any)",
                    "Show faces with emotions",
                    "Maintain consistent branding",
                    "Test different styles"
                ]
            }
        }
        
        # Calculate SEO score
        seo_score = 0
        total_factors = 0
        
        # Title length score
        if 40 <= avg_title_length <= 70:
            seo_score += 25
        elif 30 <= avg_title_length <= 80:
            seo_score += 15
        else:
            seo_score += 5
        total_factors += 25
        
        # Engagement score (proxy for SEO effectiveness)
        avg_engagement = mean([v.get('engagement_score', 0) for v in videos]) if videos else 0
        engagement_seo_score = min(avg_engagement * 2500, 25)  # Scale to 25 points max
        seo_score += engagement_seo_score
        total_factors += 25
        
        # Performance score (another SEO proxy)
        avg_performance = mean([v.get('performance_score', 0) for v in videos]) if videos else 0
        performance_seo_score = min(avg_performance / 4, 25)  # Scale to 25 points max
        seo_score += performance_seo_score
        total_factors += 25
        
        # Consistency score
        if len(videos) > 1:
            consistency_score = 25  # Assume good consistency if multiple videos
        else:
            consistency_score = 10
        seo_score += consistency_score
        total_factors += 25
        
        seo_recommendations["overall_seo_score"] = round((seo_score / total_factors) * 100, 1)
        
        return seo_recommendations
        
    except Exception as e:
        logger.error(f"Error generating SEO recommendations: {str(e)}")
        return {}

def analyze_engagement_optimization(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze engagement optimization opportunities."""
    try:
        if not videos:
            return {}
        
        avg_engagement = mean([v.get('engagement_score', 0) for v in videos])
        
        engagement_analysis = {
            "current_engagement_rate": round(avg_engagement, 4),
            "industry_benchmark": 0.035,  # 3.5% is good for most niches
            "performance_vs_benchmark": "above" if avg_engagement > 0.035 else "below",
            "optimization_strategies": [
                {
                    "strategy": "Call-to-Action Optimization",
                    "impact": "High",
                    "description": "Add clear CTAs at strategic points",
                    "implementation": [
                        "Ask questions to encourage comments",
                        "Request likes at peak engagement moments",
                        "Promote subscription with value proposition",
                        "Use end screens effectively"
                    ]
                },
                {
                    "strategy": "Content Hook Improvement",
                    "impact": "High",
                    "description": "Improve video openings to retain viewers",
                    "implementation": [
                        "Start with compelling question or statement",
                        "Preview what viewers will learn",
                        "Use pattern interrupts",
                        "Avoid long intros"
                    ]
                },
                {
                    "strategy": "Community Building",
                    "impact": "Medium",
                    "description": "Build stronger community engagement",
                    "implementation": [
                        "Respond to comments within 2 hours",
                        "Create community posts",
                        "Host live streams",
                        "Feature viewer comments in videos"
                    ]
                },
                {
                    "strategy": "Interactive Elements",
                    "impact": "Medium",
                    "description": "Add interactive features to videos",
                    "implementation": [
                        "Use polls and cards",
                        "Add clickable elements",
                        "Create choose-your-adventure style content",
                        "Include timestamps for easy navigation"
                    ]
                }
            ],
            "engagement_timeline": generate_engagement_timeline(videos),
            "top_engaging_content": identify_most_engaging_content(videos)
        }
        
        return engagement_analysis
        
    except Exception as e:
        logger.error(f"Error analyzing engagement optimization: {str(e)}")
        return {}

def identify_priority_actions(videos: List[Dict[str, Any]], channel_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Identify priority actions based on comprehensive analysis."""
    try:
        priority_actions = []
        
        if not videos:
            return [{
                "action": "Create First Video",
                "priority": 1,
                "impact": "Critical",
                "effort": "Medium",
                "timeline": "1 week"
            }]
        
        # Calculate key metrics
        avg_performance = mean([v.get('performance_score', 0) for v in videos])
        avg_engagement = mean([v.get('engagement_score', 0) for v in videos])
        total_revenue = sum(v.get('revenue_total', 0) for v in videos)
        
        # Priority 1: Critical performance issues
        if avg_performance < 30:
            priority_actions.append({
                "action": "Improve Content Quality",
                "priority": 1,
                "impact": "Critical",
                "effort": "High",
                "timeline": "2-4 weeks",
                "details": "Focus on production value, storytelling, and audience value"
            })
        
        # Priority 2: Engagement optimization
        if avg_engagement < 0.02:  # Less than 2%
            priority_actions.append({
                "action": "Boost Audience Engagement",
                "priority": 2,
                "impact": "High",
                "effort": "Medium",
                "timeline": "1-2 weeks",
                "details": "Add CTAs, improve thumbnails, respond to comments"
            })
        
        # Priority 3: Consistency
        if len(videos) < 5:
            priority_actions.append({
                "action": "Establish Consistent Upload Schedule",
                "priority": 3,
                "impact": "High",
                "effort": "Medium",
                "timeline": "Ongoing",
                "details": "Create content calendar and batch produce videos"
            })
        
        # Priority 4: Monetization
        if total_revenue < len(videos) * 50:  # Less than $50 per video
            priority_actions.append({
                "action": "Optimize Monetization Strategy",
                "priority": 4,
                "impact": "Medium",
                "effort": "Low",
                "timeline": "1 week",
                "details": "Explore sponsorships, affiliate marketing, and ad optimization"
            })
        
        # Priority 5: SEO optimization
        title_lengths = [len(v.get('title', '')) for v in videos]
        avg_title_length = mean(title_lengths) if title_lengths else 0
        
        if avg_title_length < 40 or avg_title_length > 70:
            priority_actions.append({
                "action": "Optimize SEO and Discoverability",
                "priority": 5,
                "impact": "Medium",
                "effort": "Low",
                "timeline": "1 week",
                "details": "Improve titles, descriptions, and tags for better search ranking"
            })
        
        return priority_actions[:5]  # Return top 5 priority actions
        
    except Exception as e:
        logger.error(f"Error identifying priority actions: {str(e)}")
        return []

def extract_common_patterns(videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract common patterns from high-performing videos."""
    try:
        if not videos:
            return []
        
        patterns = []
        
        # Duration patterns
        durations = [v.get('duration', 0) for v in videos]
        if durations:
            avg_duration = mean(durations)
            patterns.append({
                "type": "Duration",
                "pattern": f"Average {int(avg_duration/60)} minutes {int(avg_duration%60)} seconds",
                "confidence": 75
            })
        
        # Category patterns
        categories = [v.get('category', 'unknown') for v in videos]
        if categories:
            most_common = max(set(categories), key=categories.count)
            frequency = categories.count(most_common) / len(categories) * 100
            patterns.append({
                "type": "Category Focus",
                "pattern": f"{most_common} ({frequency:.0f}% of content)",
                "confidence": min(80, 50 + frequency)
            })
        
        # Performance patterns
        high_performers = [v for v in videos if v.get('performance_score', 0) > 70]
        if high_performers:
            avg_views = mean([v.get('views', 0) for v in high_performers])
            patterns.append({
                "type": "High Performance Threshold",
                "pattern": f"Videos with {int(avg_views):,}+ views perform best",
                "confidence": 70
            })
        
        return patterns
        
    except Exception as e:
        logger.error(f"Error extracting patterns: {str(e)}")
        return []

def generate_engagement_timeline(videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate engagement timeline data."""
    try:
        if not videos:
            return []
        
        # Sort videos by date
        sorted_videos = sorted(videos, key=lambda x: x.get('published_at', ''))
        
        timeline = []
        for i, video in enumerate(sorted_videos):
            try:
                pub_date = video.get('published_at', '')
                if pub_date:
                    if 'T' in pub_date:
                        date_obj = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                    else:
                        date_obj = datetime.strptime(pub_date, '%Y-%m-%d')
                    
                    timeline.append({
                        "date": date_obj.strftime('%Y-%m-%d'),
                        "engagement_rate": round(video.get('engagement_score', 0), 4),
                        "video_title": video.get('title', f'Video {i+1}')
                    })
            except Exception:
                continue
        
        return timeline
        
    except Exception as e:
        logger.error(f"Error generating engagement timeline: {str(e)}")
        return []

def identify_most_engaging_content(videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Identify most engaging content."""
    try:
        if not videos:
            return []
        
        # Sort by engagement score
        sorted_videos = sorted(videos, key=lambda x: x.get('engagement_score', 0), reverse=True)
        
        engaging_content = []
        for video in sorted_videos[:3]:  # Top 3 most engaging
            engaging_content.append({
                "title": video.get('title', 'Untitled'),
                "engagement_rate": round(video.get('engagement_score', 0), 4),
                "views": video.get('views', 0),
                "category": video.get('category', 'unknown'),
                "performance_score": round(video.get('performance_score', 0), 1)
            })
        
        return engaging_content
        
    except Exception as e:
        logger.error(f"Error identifying engaging content: {str(e)}")
        return []

def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
    """Flatten nested dictionary for CSV export."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # Convert list to string representation
            items.append((new_key, str(v)))
        else:
            items.append((new_key, v))
    return dict(items)

def calculate_rpm_analysis(videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Calculate Revenue Per Mille (RPM) analysis."""
    try:
        if not videos:
            return []
        
        rpm_data = []
        for video in videos:
            views = video.get('views', 0)
            revenue = video.get('revenue_total', 0)
            
            if views > 0:
                rpm = (revenue / views) * 1000  # Revenue per 1000 views
                rpm_data.append({
                    "title": video.get('title', 'Untitled'),
                    "views": views,
                    "revenue": revenue,
                    "rpm": round(rpm, 2),
                    "category": video.get('category', 'unknown')
                })
        
        # Sort by RPM
        rpm_data.sort(key=lambda x: x['rpm'], reverse=True)
        
        return rpm_data
        
    except Exception as e:
        logger.error(f"Error calculating RPM analysis: {str(e)}")
        return []

def identify_monetization_opportunities(videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Identify monetization opportunities."""
    try:
        opportunities = []
        
        if not videos:
            return [{
                "opportunity": "Start Creating Content",
                "potential_revenue": 0,
                "effort": "High",
                "timeline": "1-3 months"
            }]
        
        # High-view, low-revenue videos
        for video in videos:
            views = video.get('views', 0)
            revenue = video.get('revenue_total', 0)
            
            if views > 5000 and revenue < 50:  # High views, low revenue
                opportunities.append({
                    "opportunity": f"Monetize '{video.get('title', 'Untitled')}'",
                    "potential_revenue": round(views * 0.01, 2),  # $0.01 per view potential
                    "effort": "Low",
                    "timeline": "1-2 weeks",
                    "strategy": "Add sponsorship or affiliate links"
                })
        
        # Category-based opportunities
        category_performance = defaultdict(lambda: {"views": 0, "revenue": 0, "count": 0})
        for video in videos:
            category = video.get('category', 'unknown')
            category_performance[category]["views"] += video.get('views', 0)
            category_performance[category]["revenue"] += video.get('revenue_total', 0)
            category_performance[category]["count"] += 1
        
        for category, data in category_performance.items():
            if data["count"] >= 2:  # At least 2 videos in category
                avg_views = data["views"] / data["count"]
                avg_revenue = data["revenue"] / data["count"]
                
                if avg_views > 2000 and avg_revenue < 30:
                    opportunities.append({
                        "opportunity": f"Expand monetization in {category} category",
                        "potential_revenue": round(avg_views * 0.015 * data["count"], 2),
                        "effort": "Medium",
                        "timeline": "2-4 weeks",
                        "strategy": "Seek category-specific sponsorships"
                    })
        
        # Engagement-based opportunities
        high_engagement_videos = [v for v in videos if v.get('engagement_score', 0) > 0.04]
        if high_engagement_videos:
            total_potential = sum(v.get('views', 0) * 0.02 for v in high_engagement_videos)
            opportunities.append({
                "opportunity": "Leverage high-engagement content for premium offerings",
                "potential_revenue": round(total_potential, 2),
                "effort": "Medium",
                "timeline": "3-6 weeks",
                "strategy": "Create paid courses or exclusive content"
            })
        
        return sorted(opportunities, key=lambda x: x['potential_revenue'], reverse=True)[:5]
        
    except Exception as e:
        logger.error(f"Error identifying monetization opportunities: {str(e)}")
        return []

def calculate_audience_growth_metrics(videos: List[Dict[str, Any]], channel_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate audience growth metrics and projections."""
    try:
        if not videos:
            return {"error": "No video data available"}
        
        # Current metrics
        total_views = sum(v.get('views', 0) for v in videos)
        subscriber_count = channel_data.get('subscriber_count', 0)
        
        # Calculate growth rates
        if len(videos) >= 2:
            sorted_videos = sorted(videos, key=lambda x: x.get('published_at', ''))
            recent_views = sum(v.get('views', 0) for v in sorted_videos[-3:])
            older_views = sum(v.get('views', 0) for v in sorted_videos[:-3])
            
            if older_views > 0:
                view_growth_rate = (recent_views / len(sorted_videos[-3:]) - older_views / max(1, len(sorted_videos[:-3]))) / (older_views / max(1, len(sorted_videos[:-3])))
            else:
                view_growth_rate = 0.1  # Default 10% growth
        else:
            view_growth_rate = 0.1
        
        # Subscriber conversion rate
        conversion_rate = (subscriber_count / total_views) if total_views > 0 else 0.01
        
        # Growth projections
        monthly_projections = []
        current_monthly_views = total_views / max(1, len(videos)) * 4  # Assume 4 videos per month
        current_subscribers = subscriber_count
        
        for month in range(1, 13):  # 12 months
            projected_views = current_monthly_views * (1 + view_growth_rate) ** month
            projected_new_subscribers = projected_views * conversion_rate
            current_subscribers += projected_new_subscribers
            
            monthly_projections.append({
                "month": month,
                "projected_views": int(projected_views),
                "projected_subscribers": int(current_subscribers),
                "new_subscribers": int(projected_new_subscribers)
            })
        
        # Milestone predictions
        milestones = []
        for target in [1000, 10000, 100000, 1000000]:
            if subscriber_count < target:
                months_to_target = 0
                for projection in monthly_projections:
                    if projection["projected_subscribers"] >= target:
                        months_to_target = projection["month"]
                        break
                
                if months_to_target > 0:
                    milestones.append({
                        "target": target,
                        "months_to_reach": months_to_target,
                        "confidence": max(90 - months_to_target * 5, 30)
                    })
        
        return {
            "current_metrics": {
                "total_views": total_views,
                "subscriber_count": subscriber_count,
                "conversion_rate": round(conversion_rate, 4),
                "growth_rate": round(view_growth_rate * 100, 1)
            },
            "monthly_projections": monthly_projections,
            "milestone_predictions": milestones,
            "growth_strategies": [
                {
                    "strategy": "Improve Conversion Rate",
                    "current": f"{conversion_rate*100:.2f}%",
                    "target": "2-3%",
                    "impact": "High"
                },
                {
                    "strategy": "Increase Upload Frequency",
                    "current": f"{len(videos)} videos",
                    "target": "Weekly uploads",
                    "impact": "Medium"
                },
                {
                    "strategy": "Cross-Platform Promotion",
                    "current": "YouTube only",
                    "target": "Multi-platform presence",
                    "impact": "Medium"
                }
            ]
        }
        
    except Exception as e:
        logger.error(f"Error calculating growth metrics: {str(e)}")
        return {"error": str(e)}

def generate_competitive_analysis(videos: List[Dict[str, Any]], niche: str = "general") -> Dict[str, Any]:
    """Generate competitive analysis against industry benchmarks."""
    try:
        # Industry benchmarks (these would come from real data in production)
        benchmarks = {
            "tech": {
                "avg_views": 15000,
                "avg_engagement": 0.045,
                "avg_revenue_per_video": 150,
                "avg_duration": 720,  # 12 minutes
                "upload_frequency": 2  # per week
            },
            "gaming": {
                "avg_views": 25000,
                "avg_engagement": 0.055,
                "avg_revenue_per_video": 200,
                "avg_duration": 900,  # 15 minutes
                "upload_frequency": 3
            },
            "education": {
                "avg_views": 12000,
                "avg_engagement": 0.035,
                "avg_revenue_per_video": 100,
                "avg_duration": 600,  # 10 minutes
                "upload_frequency": 1
            },
            "general": {
                "avg_views": 10000,
                "avg_engagement": 0.035,
                "avg_revenue_per_video": 100,
                "avg_duration": 600,
                "upload_frequency": 2
            }
        }
        
        benchmark = benchmarks.get(niche.lower(), benchmarks["general"])
        
        if not videos:
            return {
                "error": "No video data for comparison",
                "benchmarks": benchmark
            }
        
        # Calculate current performance
        current_metrics = {
            "avg_views": mean([v.get('views', 0) for v in videos]),
            "avg_engagement": mean([v.get('engagement_score', 0) for v in videos]),
            "avg_revenue_per_video": mean([v.get('revenue_total', 0) for v in videos]),
            "avg_duration": mean([v.get('duration', 0) for v in videos]),
            "upload_frequency": len(videos) / 4  # Assume data spans 4 weeks
        }
        
        # Calculate performance ratios
        performance_comparison = {}
        for metric, current_value in current_metrics.items():
            benchmark_value = benchmark[metric]
            if benchmark_value > 0:
                ratio = current_value / benchmark_value
                performance_comparison[metric] = {
                    "current": round(current_value, 2),
                    "benchmark": benchmark_value,
                    "ratio": round(ratio, 2),
                    "status": "above" if ratio > 1.1 else "below" if ratio < 0.9 else "on_par"
                }
        
        # Overall competitive score
        ratios = [comp["ratio"] for comp in performance_comparison.values()]
        competitive_score = mean(ratios) * 100 if ratios else 0
        
        # Improvement recommendations
        improvement_areas = []
        for metric, comp in performance_comparison.items():
            if comp["ratio"] < 0.8:  # 20% below benchmark
                improvement_areas.append({
                    "metric": metric.replace('_', ' ').title(),
                    "gap": f"{(1 - comp['ratio']) * 100:.0f}% below benchmark",
                    "priority": "high" if comp["ratio"] < 0.5 else "medium"
                })
        
        return {
            "niche": niche,
            "competitive_score": round(competitive_score, 1),
            "performance_comparison": performance_comparison,
            "improvement_areas": improvement_areas,
            "strengths": [
                metric.replace('_', ' ').title() 
                for metric, comp in performance_comparison.items() 
                if comp["ratio"] > 1.2
            ],
            "market_position": (
                "Leading" if competitive_score > 120 else
                "Competitive" if competitive_score > 80 else
                "Developing" if competitive_score > 50 else
                "Emerging"
            )
        }
        
    except Exception as e:
        logger.error(f"Error generating competitive analysis: {str(e)}")
        return {"error": str(e)}

def calculate_content_roi(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate Return on Investment for content creation."""
    try:
        if not videos:
            return {"error": "No video data available"}
        
        # Estimate production costs (these would be actual costs in production)
        estimated_costs_per_video = {
            "time_cost": 200,  # $200 worth of time per video
            "equipment_cost": 20,  # Amortized equipment cost
            "software_cost": 10,  # Software subscriptions
            "other_costs": 20  # Miscellaneous
        }
        
        total_cost_per_video = sum(estimated_costs_per_video.values())
        
        # Calculate ROI for each video
        video_roi = []
        for video in videos:
            revenue = video.get('revenue_total', 0)
            roi_percentage = ((revenue - total_cost_per_video) / total_cost_per_video) * 100 if total_cost_per_video > 0 else 0
            
            video_roi.append({
                "title": video.get('title', 'Untitled'),
                "revenue": revenue,
                "estimated_cost": total_cost_per_video,
                "profit": revenue - total_cost_per_video,
                "roi_percentage": round(roi_percentage, 1),
                "views": video.get('views', 0),
                "revenue_per_view": round(revenue / video.get('views', 1), 4)
            })
        
        # Overall ROI metrics
        total_revenue = sum(v.get('revenue_total', 0) for v in videos)
        total_cost = len(videos) * total_cost_per_video
        overall_roi = ((total_revenue - total_cost) / total_cost) * 100 if total_cost > 0 else 0
        
        # ROI by category
        category_roi = defaultdict(lambda: {"revenue": 0, "cost": 0, "count": 0})
        for video in videos:
            category = video.get('category', 'unknown')
            category_roi[category]["revenue"] += video.get('revenue_total', 0)
            category_roi[category]["cost"] += total_cost_per_video
            category_roi[category]["count"] += 1
        
        category_analysis = []
        for category, data in category_roi.items():
            roi = ((data["revenue"] - data["cost"]) / data["cost"]) * 100 if data["cost"] > 0 else 0
            category_analysis.append({
                "category": category,
                "roi_percentage": round(roi, 1),
                "total_profit": round(data["revenue"] - data["cost"], 2),
                "video_count": data["count"]
            })
        
        return {
            "overall_roi": {
                "roi_percentage": round(overall_roi, 1),
                "total_revenue": round(total_revenue, 2),
                "total_cost": round(total_cost, 2),
                "total_profit": round(total_revenue - total_cost, 2)
            },
            "video_roi": sorted(video_roi, key=lambda x: x['roi_percentage'], reverse=True),
            "category_roi": sorted(category_analysis, key=lambda x: x['roi_percentage'], reverse=True),
            "cost_breakdown": estimated_costs_per_video,
            "profitability_threshold": {
                "break_even_revenue": total_cost_per_video,
                "profitable_videos": len([v for v in video_roi if v['profit'] > 0]),
                "loss_making_videos": len([v for v in video_roi if v['profit'] <= 0])
            }
        }
        
    except Exception as e:
        logger.error(f"Error calculating content ROI: {str(e)}")
        return {"error": str(e)}

def generate_advanced_insights(videos: List[Dict[str, Any]], channel_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate advanced insights combining multiple analysis methods."""
    try:
        insights = {
            "performance_insights": [],
            "growth_insights": [],
            "monetization_insights": [],
            "content_insights": [],
            "strategic_recommendations": []
        }
        
        if not videos:
            insights["strategic_recommendations"].append({
                "type": "foundation",
                "insight": "Start creating content to build analytics foundation",
                "priority": "critical",
                "impact": "high"
            })
            return insights
        
        # Performance insights
        performance_scores = [v.get('performance_score', 0) for v in videos]
        avg_performance = mean(performance_scores)
        performance_trend = "improving" if len(performance_scores) > 1 and performance_scores[-1] > performance_scores[0] else "declining"
        
        insights["performance_insights"].append({
            "metric": "Overall Performance",
            "value": round(avg_performance, 1),
            "trend": performance_trend,
            "insight": f"Channel performance is {performance_trend} with an average score of {avg_performance:.1f}/100"
        })
        
        # Identify performance outliers
        if len(performance_scores) > 2:
            performance_std = stdev(performance_scores)
            outliers = [v for v in videos if abs(v.get('performance_score', 0) - avg_performance) > performance_std * 2]
            if outliers:
                insights["performance_insights"].append({
                    "metric": "Performance Consistency",
                    "value": f"{len(outliers)} outliers",
                    "trend": "variable",
                    "insight": f"Found {len(outliers)} videos with significantly different performance - analyze for patterns"
                })
        
        # Growth insights
        total_views = sum(v.get('views', 0) for v in videos)
        subscriber_count = channel_data.get('subscriber_count', 0)
        conversion_rate = (subscriber_count / total_views) if total_views > 0 else 0
        
        insights["growth_insights"].append({
            "metric": "Subscriber Conversion Rate",
            "value": f"{conversion_rate*100:.2f}%",
            "trend": "good" if conversion_rate > 0.02 else "needs_improvement",
            "insight": f"Converting {conversion_rate*100:.2f}% of viewers to subscribers" + 
                      (" - above average" if conversion_rate > 0.02 else " - below 2% benchmark")
        })
        
        # View velocity analysis
        if len(videos) >= 3:
            recent_avg_views = mean([v.get('views', 0) for v in videos[-3:]])
            older_avg_views = mean([v.get('views', 0) for v in videos[:-3]])
            view_growth = ((recent_avg_views - older_avg_views) / older_avg_views) * 100 if older_avg_views > 0 else 0
            
            insights["growth_insights"].append({
                "metric": "View Growth Velocity",
                "value": f"{view_growth:+.1f}%",
                "trend": "positive" if view_growth > 0 else "negative",
                "insight": f"Recent videos are getting {abs(view_growth):.1f}% {'more' if view_growth > 0 else 'fewer'} views on average"
            })
        
        # Monetization insights
        total_revenue = sum(v.get('revenue_total', 0) for v in videos)
        revenue_per_view = total_revenue / total_views if total_views > 0 else 0
        
        insights["monetization_insights"].append({
            "metric": "Revenue Per View",
            "value": f"${revenue_per_view:.4f}",
            "trend": "good" if revenue_per_view > 0.01 else "needs_improvement",
            "insight": f"Earning ${revenue_per_view:.4f} per view" + 
                      (" - strong monetization" if revenue_per_view > 0.01 else " - monetization opportunity exists")
        })
        
        # Revenue stream analysis
        ad_revenue = sum(v.get('ad_revenue', 0) for v in videos)
        sponsorship_revenue = sum(v.get('sponsorship_revenue', 0) for v in videos)
        affiliate_revenue = sum(v.get('affiliate_revenue', 0) for v in videos)
        
        revenue_streams = [
            ("Ad Revenue", ad_revenue),
            ("Sponsorship", sponsorship_revenue),
            ("Affiliate", affiliate_revenue)
        ]
        
        dominant_stream = max(revenue_streams, key=lambda x: x[1])
        insights["monetization_insights"].append({
            "metric": "Revenue Diversification",
            "value": dominant_stream[0],
            "trend": "concentrated" if dominant_stream[1] / total_revenue > 0.7 else "diversified",
            "insight": f"{dominant_stream[0]} is the primary revenue source ({dominant_stream[1]/total_revenue*100:.0f}% of total)"
        })
        
        # Content insights
        categories = [v.get('category', 'unknown') for v in videos]
        category_counts = {cat: categories.count(cat) for cat in set(categories)}
        most_common_category = max(category_counts, key=category_counts.get)
        
        insights["content_insights"].append({
            "metric": "Content Focus",
            "value": most_common_category,
            "trend": "focused" if category_counts[most_common_category] / len(videos) > 0.6 else "diverse",
            "insight": f"{most_common_category} represents {category_counts[most_common_category]/len(videos)*100:.0f}% of content"
        })
        
        # Duration analysis
        durations = [v.get('duration', 0) for v in videos]
        avg_duration = mean(durations)
        duration_category = (
            "Short-form" if avg_duration < 300 else
            "Medium-form" if avg_duration < 900 else
            "Long-form"
        )
        
        insights["content_insights"].append({
            "metric": "Content Length Strategy",
            "value": f"{int(avg_duration/60)}:{int(avg_duration%60):02d}",
            "trend": duration_category.lower(),
            "insight": f"Focusing on {duration_category.lower()} content with average length of {int(avg_duration/60)} minutes"
        })
        
        # Strategic recommendations based on insights
        recommendations = []
        
        # Performance-based recommendations
        if avg_performance < 50:
            recommendations.append({
                "type": "performance",
                "insight": "Focus on content quality improvement",
                "priority": "high",
                "impact": "high",
                "action": "Analyze top-performing videos and replicate successful elements"
            })
        
        # Growth-based recommendations
        if conversion_rate < 0.015:  # Less than 1.5%
            recommendations.append({
                "type": "growth",
                "insight": "Improve subscriber conversion rate",
                "priority": "high",
                "impact": "medium",
                "action": "Add stronger calls-to-action and value propositions for subscribing"
            })
        
        # Monetization recommendations
        if revenue_per_view < 0.005:  # Less than $0.005 per view
            recommendations.append({
                "type": "monetization",
                "insight": "Explore additional revenue streams",
                "priority": "medium",
                "impact": "high",
                "action": "Investigate sponsorship opportunities and affiliate partnerships"
            })
        
        # Content strategy recommendations
        if len(set(categories)) == 1 and len(videos) > 5:
            recommendations.append({
                "type": "content",
                "insight": "Consider content diversification",
                "priority": "low",
                "impact": "medium",
                "action": "Test related content categories to expand audience reach"
            })
        elif len(set(categories)) > len(videos) * 0.8:
            recommendations.append({
                "type": "content",
                "insight": "Focus content strategy",
                "priority": "medium",
                "impact": "medium",
                "action": "Identify best-performing categories and create more content in those areas"
            })
        
        insights["strategic_recommendations"] = recommendations
        
        return insights
        
    except Exception as e:
        logger.error(f"Error generating advanced insights: {str(e)}")
        return {"error": str(e)}

def export_analytics_data(analytics_data: Dict[str, Any], format: str = "json") -> str:
    """Export analytics data in specified format."""
    try:
        if format.lower() == "json":
            return json.dumps(analytics_data, indent=2, default=str)
        
        elif format.lower() == "csv":
            # Flatten the data for CSV export
            flattened_data = flatten_dict(analytics_data)
            
            # Create CSV content
            csv_content = "Metric,Value\n"
            for key, value in flattened_data.items():
                csv_content += f'"{key}","{value}"\n'
            
            return csv_content
        
        elif format.lower() == "txt":
            # Create readable text report
            def format_section(data, level=0):
                indent = "  " * level
                result = ""
                
                if isinstance(data, dict):
                    for key, value in data.items():
                        result += f"{indent}{key.replace('_', ' ').title()}:\n"
                        if isinstance(value, (dict, list)):
                            result += format_section(value, level + 1)
                        else:
                            result += f"{indent}  {value}\n"
                elif isinstance(data, list):
                    for i, item in enumerate(data):
                        result += f"{indent}Item {i + 1}:\n"
                        result += format_section(item, level + 1)
                else:
                    result += f"{indent}{data}\n"
                
                return result
            
            return format_section(analytics_data)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
    except Exception as e:
        logger.error(f"Error exporting analytics data: {str(e)}")
        return f"Error exporting data: {str(e)}"

# Utility functions for statistical calculations
def calculate_percentile(data: List[float], percentile: float) -> float:
    """Calculate percentile of a dataset."""
    if not data:
        return 0
    
    sorted_data = sorted(data)
    index = (percentile / 100) * (len(sorted_data) - 1)
    
    if index.is_integer():
        return sorted_data[int(index)]
    else:
        lower_index = int(index)
        upper_index = lower_index + 1
        weight = index - lower_index
        return sorted_data[lower_index] * (1 - weight) + sorted_data[upper_index] * weight

def calculate_correlation(x: List[float], y: List[float]) -> float:
    """Calculate correlation coefficient between two datasets."""
    if len(x) != len(y) or len(x) < 2:
        return 0
    
    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(x[i] * y[i] for i in range(n))
    sum_x2 = sum(xi * xi for xi in x)
    sum_y2 = sum(yi * yi for yi in y)
    
    numerator = n * sum_xy - sum_x * sum_y
    denominator = ((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y)) ** 0.5
    
    return numerator / denominator if denominator != 0 else 0

def detect_anomalies(data: List[float], threshold: float = 2.0) -> List[int]:
    """Detect anomalies in data using z-score method."""
    if len(data) < 3:
        return []
    
    data_mean = mean(data)
    data_std = stdev(data)
    
    if data_std == 0:
        return []
    
    anomalies = []
    for i, value in enumerate(data):
        z_score = abs(value - data_mean) / data_std
        if z_score > threshold:
            anomalies.append(i)
    
    return anomalies

def calculate_moving_average(data: List[float], window: int = 3) -> List[float]:
    """Calculate moving average of data."""
    if len(data) < window:
        return data
    
    moving_averages = []
    for i in range(len(data) - window + 1):
        window_data = data[i:i + window]
        moving_averages.append(mean(window_data))
    
    return moving_averages

def generate_summary_statistics(data: List[float]) -> Dict[str, float]:
    """Generate comprehensive summary statistics."""
    if not data:
        return {}
    
    sorted_data = sorted(data)
    
    return {
        "count": len(data),
        "mean": round(mean(data), 2),
        "median": round(sorted_data[len(sorted_data) // 2], 2),
        "mode": round(max(set(data), key=data.count), 2) if data else 0,
        "std_dev": round(stdev(data) if len(data) > 1 else 0, 2),
        "variance": round(stdev(data) ** 2 if len(data) > 1 else 0, 2),
        "min": round(min(data), 2),
        "max": round(max(data), 2),
        "range": round(max(data) - min(data), 2),
        "q1": round(calculate_percentile(data, 25), 2),
        "q3": round(calculate_percentile(data, 75), 2),
        "iqr": round(calculate_percentile(data, 75) - calculate_percentile(data, 25), 2)
    }