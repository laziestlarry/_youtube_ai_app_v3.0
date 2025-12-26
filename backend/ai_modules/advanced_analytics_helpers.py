"""
Advanced Analytics Helper Functions
Provides utility functions for complex analytics calculations and data processing.
"""

import math
import statistics
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter
import logging

logger = logging.getLogger(__name__)

class AnalyticsCalculator:
    """Advanced analytics calculation engine."""
    
    def __init__(self):
        self.benchmark_data = self._load_benchmark_data()
    
    def _load_benchmark_data(self) -> Dict[str, Any]:
        """Load industry benchmark data for comparisons."""
        return {
            "average_ctr": 0.045,
            "average_engagement": 0.035,
            "average_retention": 0.65,
            "category_benchmarks": {
                "tech": {"engagement": 0.042, "retention": 0.68},
                "gaming": {"engagement": 0.055, "retention": 0.72},
                "education": {"engagement": 0.038, "retention": 0.75},
                "entertainment": {"engagement": 0.048, "retention": 0.58},
                "lifestyle": {"engagement": 0.041, "retention": 0.62}
            }
        }
    
    def calculate_engagement_quality_score(self, videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate comprehensive engagement quality metrics."""
        try:
            if not videos:
                return {"error": "No video data available"}
            
            engagement_metrics = []
            for video in videos:
                views = video.get("views", 0)
                likes = video.get("likes", views * 0.035)  # Estimated if not provided
                comments = video.get("comments", views * 0.008)
                shares = video.get("shares", views * 0.002)
                
                if views > 0:
                    engagement_rate = (likes + comments * 2 + shares * 3) / views
                    quality_score = min(100, engagement_rate * 1000)  # Scale to 0-100
                    
                    engagement_metrics.append({
                        "video_title": video.get("title", "Unknown"),
                        "engagement_rate": engagement_rate,
                        "quality_score": quality_score,
                        "likes_ratio": likes / views,
                        "comments_ratio": comments / views,
                        "shares_ratio": shares / views
                    })
            
            if not engagement_metrics:
                return {"error": "No valid engagement data"}
            
            # Calculate aggregate metrics
            avg_engagement = statistics.mean([m["engagement_rate"] for m in engagement_metrics])
            avg_quality = statistics.mean([m["quality_score"] for m in engagement_metrics])
            
            # Determine engagement tier
            if avg_quality >= 80:
                tier = "exceptional"
            elif avg_quality >= 60:
                tier = "good"
            elif avg_quality >= 40:
                tier = "average"
            else:
                tier = "needs_improvement"
            
            return {
                "overall_engagement_rate": round(avg_engagement, 4),
                "quality_score": round(avg_quality, 1),
                "engagement_tier": tier,
                "video_metrics": engagement_metrics,
                "benchmark_comparison": {
                    "vs_industry_average": round((avg_engagement / self.benchmark_data["average_engagement"] - 1) * 100, 1),
                    "performance_rating": "above_average" if avg_engagement > self.benchmark_data["average_engagement"] else "below_average"
                },
                "improvement_potential": max(0, round((self.benchmark_data["average_engagement"] - avg_engagement) * 1000, 1))
            }
            
        except Exception as e:
            logger.error(f"Error calculating engagement quality score: {str(e)}")
            return {"error": str(e)}
    
    def analyze_content_lifecycle(self, videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze content performance lifecycle patterns."""
        try:
            if len(videos) < 5:
                return {"error": "Insufficient data for lifecycle analysis"}
            
            # Sort videos by publication date
            sorted_videos = sorted(videos, key=lambda x: x.get("published_at", ""))
            
            lifecycle_stages = {
                "launch": sorted_videos[:len(sorted_videos)//4] or sorted_videos[:1],
                "growth": sorted_videos[len(sorted_videos)//4:len(sorted_videos)//2] or sorted_videos[1:2],
                "maturity": sorted_videos[len(sorted_videos)//2:3*len(sorted_videos)//4] or sorted_videos[2:3],
                "optimization": sorted_videos[3*len(sorted_videos)//4:] or sorted_videos[3:]
            }
            
            stage_analysis = {}
            for stage, stage_videos in lifecycle_stages.items():
                if stage_videos:
                    avg_performance = statistics.mean([v.get("performance_score", 0) for v in stage_videos])
                    avg_views = statistics.mean([v.get("views", 0) for v in stage_videos])
                    avg_engagement = statistics.mean([v.get("engagement_score", 0) for v in stage_videos])
                    
                    stage_analysis[stage] = {
                        "video_count": len(stage_videos),
                        "avg_performance": round(avg_performance, 1),
                        "avg_views": int(avg_views),
                        "avg_engagement": round(avg_engagement, 4),
                        "performance_trend": self._calculate_trend([v.get("performance_score", 0) for v in stage_videos])
                    }
            
            # Identify lifecycle patterns
            performance_progression = [stage_analysis[stage]["avg_performance"] for stage in ["launch", "growth", "maturity", "optimization"] if stage in stage_analysis]
            
            if len(performance_progression) >= 3:
                if performance_progression[-1] > performance_progression[0]:
                    lifecycle_pattern = "improving"
                elif performance_progression[-1] < performance_progression[0] * 0.8:
                    lifecycle_pattern = "declining"
                else:
                    lifecycle_pattern = "stable"
            else:
                lifecycle_pattern = "insufficient_data"
            
            return {
                "lifecycle_pattern": lifecycle_pattern,
                "stage_analysis": stage_analysis,
                "performance_progression": performance_progression,
                "recommendations": self._generate_lifecycle_recommendations(lifecycle_pattern, stage_analysis),
                "next_stage_prediction": self._predict_next_stage_performance(stage_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing content lifecycle: {str(e)}")
            return {"error": str(e)}
    
    def calculate_roi_efficiency(self, videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate return on investment efficiency metrics."""
        try:
            if not videos:
                return {"error": "No video data available"}
            
            roi_metrics = []
            total_investment = 0
            total_revenue = 0
            
            for video in videos:
                # Estimate production cost based on duration and quality
                duration = video.get("duration", 600)  # Default 10 minutes
                estimated_cost = self._estimate_production_cost(duration, video.get("category", "general"))
                
                revenue = video.get("revenue_total", 0)
                if revenue == 0:
                    # Estimate revenue from views
                    views = video.get("views", 0)
                    revenue = views * 0.003  # $3 per 1000 views estimate
                
                roi = ((revenue - estimated_cost) / estimated_cost * 100) if estimated_cost > 0 else 0
                efficiency = revenue / estimated_cost if estimated_cost > 0 else 0
                
                roi_metrics.append({
                    "title": video.get("title", "Unknown"),
                    "estimated_cost": estimated_cost,
                    "revenue": revenue,
                    "roi_percentage": round(roi, 1),
                    "efficiency_ratio": round(efficiency, 2),
                    "profit": round(revenue - estimated_cost, 2)
                })
                
                total_investment += estimated_cost
                total_revenue += revenue
            
            # Calculate aggregate ROI metrics
            overall_roi = ((total_revenue - total_investment) / total_investment * 100) if total_investment > 0 else 0
            avg_efficiency = statistics.mean([m["efficiency_ratio"] for m in roi_metrics])
            
            # Identify most/least profitable content
            profitable_videos = [m for m in roi_metrics if m["roi_percentage"] > 0]
            loss_making_videos = [m for m in roi_metrics if m["roi_percentage"] < 0]
            
            return {
                "overall_roi": round(overall_roi, 1),
                "total_investment": round(total_investment, 2),
                "total_revenue": round(total_revenue, 2),
                "net_profit": round(total_revenue - total_investment, 2),
                "average_efficiency": round(avg_efficiency, 2),
                "profitable_content_ratio": round(len(profitable_videos) / len(roi_metrics) * 100, 1),
                "video_roi_analysis": sorted(roi_metrics, key=lambda x: x["roi_percentage"], reverse=True),
                "top_performers": sorted(roi_metrics, key=lambda x: x["roi_percentage"], reverse=True)[:3],
                "underperformers": sorted(roi_metrics, key=lambda x: x["roi_percentage"])[:3],
                "optimization_opportunities": self._identify_roi_optimization_opportunities(roi_metrics)
            }
            
        except Exception as e:
            logger.error(f"Error calculating ROI efficiency: {str(e)}")
            return {"error": str(e)}
    
    def analyze_audience_retention_patterns(self, videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze audience retention and viewing patterns."""
        try:
            if not videos:
                return {"error": "No video data available"}
            
            retention_analysis = []
            for video in videos:
                duration = video.get("duration", 600)
                views = video.get("views", 0)
                
                # Estimate retention curve (in real implementation, use YouTube Analytics API)
                estimated_retention = self._estimate_retention_curve(duration, video.get("category", "general"))
                
                # Calculate key retention metrics
                avg_view_duration = duration * estimated_retention["average_retention"]
                retention_score = estimated_retention["average_retention"] * 100
                
                retention_analysis.append({
                    "title": video.get("title", "Unknown"),
                    "duration_minutes": round(duration / 60, 1),
                    "average_retention": round(estimated_retention["average_retention"], 3),
                    "retention_score": round(retention_score, 1),
                    "avg_view_duration": round(avg_view_duration / 60, 1),
                    "drop_off_points": estimated_retention["drop_off_points"],
                    "engagement_peaks": estimated_retention["engagement_peaks"]
                })
            
            # Calculate aggregate retention metrics
            overall_retention = statistics.mean([r["average_retention"] for r in retention_analysis])
            retention_consistency = 1 - (statistics.stdev([r["average_retention"] for r in retention_analysis]) / overall_retention) if overall_retention > 0 else 0
            
            # Identify patterns
            duration_vs_retention = self._analyze_duration_retention_correlation(retention_analysis)
            optimal_content_length = self._find_optimal_content_length(retention_analysis)
            
            return {
                "overall_retention_rate": round(overall_retention, 3),
                "retention_score": round(overall_retention * 100, 1),
                "retention_consistency": round(retention_consistency, 3),
                "video_retention_analysis": retention_analysis,
                "duration_correlation": duration_vs_retention,
                "optimal_length_recommendation": optimal_content_length,
                "retention_improvement_tips": self._generate_retention_tips(retention_analysis),
                "benchmark_comparison": {
                    "vs_category_average": round((overall_retention / 0.65 - 1) * 100, 1),  # 65% industry average
                    "performance_tier": self._determine_retention_tier(overall_retention)
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing audience retention: {str(e)}")
            return {"error": str(e)}
    
    def predict_viral_potential(self, videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict viral potential of content based on early performance indicators."""
        try:
            if not videos:
                return {"error": "No video data available"}
            
            viral_analysis = []
            for video in videos:
                # Calculate viral indicators
                views = video.get("views", 0)
                engagement_rate = video.get("engagement_score", 0)
                shares = video.get("shares", views * 0.002)  # Estimated if not provided
                
                # Viral potential factors
                factors = {
                    "engagement_velocity": min(engagement_rate * 1000, 100),
                    "share_ratio": min((shares / views * 1000) if views > 0 else 0, 100),
                    "early_performance": min((views / 1000), 100),  # Views in first period
                    "content_quality": video.get("performance_score", 50),
                    "trending_topic_alignment": self._assess_trending_alignment(video.get("title", ""))
                }
                
                # Calculate viral potential score
                viral_score = statistics.mean(list(factors.values()))
                
                # Determine viral probability
                if viral_score >= 80:
                    viral_probability = "high"
                    probability_percentage = 75
                elif viral_score >= 60:
                    viral_probability = "medium"
                    probability_percentage = 45
                elif viral_score >= 40:
                    viral_probability = "low"
                    probability_percentage = 20
                else:
                    viral_probability = "very_low"
                    probability_percentage = 5
                
                viral_analysis.append({
                    "title": video.get("title", "Unknown"),
                    "viral_score": round(viral_score, 1),
                    "viral_probability": viral_probability,
                    "probability_percentage": probability_percentage,
                    "key_factors": factors,
                    "optimization_suggestions": self._generate_viral_optimization_tips(factors)
                })
            
            # Identify content with highest viral potential
            top_viral_candidates = sorted(viral_analysis, key=lambda x: x["viral_score"], reverse=True)[:3]
            
            return {
                "viral_analysis": viral_analysis,
                "top_viral_candidates": top_viral_candidates,
                "overall_viral_readiness": round(statistics.mean([v["viral_score"] for v in viral_analysis]), 1),
                "viral_optimization_strategy": self._create_viral_strategy(viral_analysis),
                "success_indicators": self._identify_viral_success_patterns(viral_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error predicting viral potential: {str(e)}")
            return {"error": str(e)}
    
    def analyze_competitive_positioning(self, videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze competitive positioning and market share potential."""
        try:
            if not videos:
                return {"error": "No video data available"}
            
            # Analyze content categories and performance
            category_performance = defaultdict(lambda: {"videos": [], "total_views": 0, "avg_performance": 0})
            
            for video in videos:
                category = video.get("category", "unknown")
                category_performance[category]["videos"].append(video)
                category_performance[category]["total_views"] += video.get("views", 0)
                category_performance[category]["avg_performance"] += video.get("performance_score", 0)
            
            # Calculate competitive metrics for each category
            competitive_analysis = {}
            for category, data in category_performance.items():
                video_count = len(data["videos"])
                avg_performance = data["avg_performance"] / video_count if video_count > 0 else 0
                
                # Estimate market position
                market_position = self._estimate_market_position(category, avg_performance, data["total_views"])
                
                competitive_analysis[category] = {
                    "video_count": video_count,
                    "total_views": data["total_views"],
                    "avg_performance": round(avg_performance, 1),
                    "market_position": market_position,
                    "competitive_strength": self._calculate_competitive_strength(category, data),
                    "growth_opportunity": self._assess_growth_opportunity(category, data)
                }
            
            # Overall competitive assessment
            overall_strength = statistics.mean([cat["competitive_strength"] for cat in competitive_analysis.values()])
            dominant_category = max(competitive_analysis.items(), key=lambda x: x[1]["competitive_strength"])
            
            return {
                "competitive_analysis": competitive_analysis,
                "overall_competitive_strength": round(overall_strength, 1),
                "dominant_category": {
                    "category": dominant_category[0],
                    "strength": dominant_category[1]["competitive_strength"]
                },
                "market_opportunities": self._identify_market_opportunities_detailed(competitive_analysis),
                "competitive_advantages": self._identify_competitive_advantages(videos, competitive_analysis),
                "strategic_recommendations": self._generate_competitive_strategy(competitive_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing competitive positioning: {str(e)}")
            return {"error": str(e)}
    
    # Helper methods
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a list of values."""
        if len(values) < 2:
            return "insufficient_data"
        
        # Simple linear trend calculation
        x = list(range(len(values)))
        n = len(values)
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(xi ** 2 for xi in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2) if (n * sum_x2 - sum_x ** 2) != 0 else 0
        
        if slope > 0.1:
            return "strongly_increasing"
        elif slope > 0:
            return "increasing"
        elif slope < -0.1:
            return "strongly_decreasing"
        elif slope < 0:
            return "decreasing"
        else:
            return "stable"
    
    def _estimate_production_cost(self, duration: int, category: str) -> float:
        """Estimate production cost based on duration and category."""
        base_cost_per_minute = {
            "tech": 15.0,
            "gaming": 8.0,
            "education": 12.0,
            "entertainment": 20.0,
            "lifestyle": 10.0,
            "business": 18.0
        }.get(category, 12.0)
        
        duration_minutes = duration / 60
        return base_cost_per_minute * duration_minutes + 50  # Base setup cost
    
    def _estimate_retention_curve(self, duration: int, category: str) -> Dict[str, Any]:
        """Estimate audience retention curve based on content characteristics."""
        # Category-based retention patterns
        category_retention = {
            "tech": 0.68,
            "gaming": 0.72,
            "education": 0.75,
            "entertainment": 0.58,
            "lifestyle": 0.62,
            "business": 0.65
        }.get(category, 0.65)
        
        # Duration impact on retention
        duration_minutes = duration / 60
        if duration_minutes < 5:
            duration_factor = 1.1  # Short videos retain better
        elif duration_minutes < 15:
            duration_factor = 1.0
        elif duration_minutes < 30:
            duration_factor = 0.9
        else:
            duration_factor = 0.8
        
        adjusted_retention = min(0.95, category_retention * duration_factor)
        
        # Simulate drop-off points and engagement peaks
        drop_off_points = [
            {"timestamp": "0:15", "retention": 0.85},
            {"timestamp": f"{int(duration_minutes * 0.3)}:{int((duration_minutes * 0.3 % 1) * 60):02d}", "retention": 0.70},
            {"timestamp": f"{int(duration_minutes * 0.7)}:{int((duration_minutes * 0.7 % 1) * 60):02d}", "retention": 0.45}
        ]
        
        engagement_peaks = [
            {"timestamp": "0:30", "engagement_boost": 1.2},
            {"timestamp": f"{int(duration_minutes * 0.5)}:{int((duration_minutes * 0.5 % 1) * 60):02d}", "engagement_boost": 1.15}
        ]
        
        return {
            "average_retention": adjusted_retention,
            "drop_off_points": drop_off_points,
            "engagement_peaks": engagement_peaks
        }
    
    def _analyze_duration_retention_correlation(self, retention_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze correlation between video duration and retention."""
        if len(retention_data) < 3:
            return {"correlation": "insufficient_data"}
        
        durations = [r["duration_minutes"] for r in retention_data]
        retentions = [r["average_retention"] for r in retention_data]
        
        # Calculate correlation coefficient
        n = len(durations)
        sum_d = sum(durations)
        sum_r = sum(retentions)
        sum_dr = sum(durations[i] * retentions[i] for i in range(n))
        sum_d2 = sum(d ** 2 for d in durations)
        sum_r2 = sum(r ** 2 for r in retentions)
        
        denominator = math.sqrt((n * sum_d2 - sum_d ** 2) * (n * sum_r2 - sum_r ** 2))
        correlation = (n * sum_dr - sum_d * sum_r) / denominator if denominator != 0 else 0
        
        # Interpret correlation
        if correlation > 0.7:
            interpretation = "strong_positive"
        elif correlation > 0.3:
            interpretation = "moderate_positive"
        elif correlation > -0.3:
            interpretation = "weak_correlation"
        elif correlation > -0.7:
            interpretation = "moderate_negative"
        else:
            interpretation = "strong_negative"
        
        return {
            "correlation_coefficient": round(correlation, 3),
            "interpretation": interpretation,
            "recommendation": self._get_duration_recommendation(correlation)
        }
    
    def _find_optimal_content_length(self, retention_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find optimal content length based on retention performance."""
        if not retention_data:
            return {"optimal_length": "unknown"}
        
        # Group by duration ranges
        duration_groups = {
            "short": [r for r in retention_data if r["duration_minutes"] < 5],
            "medium": [r for r in retention_data if 5 <= r["duration_minutes"] < 15],
            "long": [r for r in retention_data if r["duration_minutes"] >= 15]
        }
        
        group_performance = {}
        for group_name, group_data in duration_groups.items():
            if group_data:
                avg_retention = statistics.mean([r["average_retention"] for r in group_data])
                avg_score = statistics.mean([r["retention_score"] for r in group_data])
                group_performance[group_name] = {
                    "avg_retention": avg_retention,
                    "avg_score": avg_score,
                    "video_count": len(group_data)
                }
        
        # Find best performing group
        if group_performance:
            best_group = max(group_performance.items(), key=lambda x: x[1]["avg_retention"])
            
            return {
                "optimal_length_category": best_group[0],
                "optimal_retention": round(best_group[1]["avg_retention"], 3),
                "group_analysis": group_performance,
                "recommendation": self._get_length_recommendation(best_group[0])
            }
        
        return {"optimal_length": "insufficient_data"}
    
    def _generate_retention_tips(self, retention_data: List[Dict[str, Any]]) -> List[str]:
        """Generate retention improvement tips based on analysis."""
        tips = []
        
        avg_retention = statistics.mean([r["average_retention"] for r in retention_data])
        
        if avg_retention < 0.5:
            tips.extend([
                "Focus on stronger video openings to hook viewers",
                "Improve content pacing and remove slow sections",
                "Add more engaging visuals and animations",
                "Create clear content structure with previews"
            ])
        elif avg_retention < 0.7:
            tips.extend([
                "Optimize mid-video engagement with interactive elements",
                "Use pattern interrupts to maintain attention",
                "Improve audio quality and pacing",
                "Add strategic calls-to-action"
            ])
        else:
            tips.extend([
                "Maintain current high-quality content approach",
                "Experiment with longer-form content",
                "Focus on building series and connected content",
                "Leverage high retention for audience growth"
            ])
        
        return tips
    
    def _determine_retention_tier(self, retention_rate: float) -> str:
        """Determine retention performance tier."""
        if retention_rate >= 0.8:
            return "exceptional"
        elif retention_rate >= 0.7:
            return "excellent"
        elif retention_rate >= 0.6:
            return "good"
        elif retention_rate >= 0.5:
            return "average"
        else:
            return "needs_improvement"
    
    def _assess_trending_alignment(self, title: str) -> float:
        """Assess how well content aligns with trending topics."""
        # Simulate trending topic analysis
        trending_keywords = [
            "ai", "artificial intelligence", "tutorial", "review", "2024",
            "tips", "guide", "how to", "best", "new", "latest", "trending"
        ]
        
        title_lower = title.lower()
        alignment_score = 0
        
        for keyword in trending_keywords:
            if keyword in title_lower:
                alignment_score += 10
        
        return min(100, alignment_score)
    
    def _generate_viral_optimization_tips(self, factors: Dict[str, float]) -> List[str]:
        """Generate tips to optimize viral potential."""
        tips = []
        
        if factors["engagement_velocity"] < 50:
            tips.append("Increase early engagement with stronger hooks and calls-to-action")
        
        if factors["share_ratio"] < 30:
            tips.append("Create more shareable content with emotional impact")
        
        if factors["trending_topic_alignment"] < 40:
            tips.append("Incorporate trending topics and keywords")
        
        if factors["content_quality"] < 60:
            tips.append("Improve production quality and storytelling")
        
        if not tips:
            tips.append("Content shows strong viral potential - maintain current approach")
        
        return tips
    
    def _create_viral_strategy(self, viral_analysis: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create comprehensive viral content strategy."""
        high_potential_count = len([v for v in viral_analysis if v["viral_probability"] in ["high", "medium"]])
        
        strategy = {
            "focus_areas": [],
            "content_optimization": [],
            "distribution_strategy": [],
            "timeline": "4-6 weeks"
        }
        
        if high_potential_count > 0:
            strategy["focus_areas"].append("Scale successful content patterns")
            strategy["content_optimization"].append("Replicate high-performing content elements")
        else:
            strategy["focus_areas"].append("Improve fundamental content quality")
            strategy["content_optimization"].append("Focus on engagement and shareability")
        
        strategy["distribution_strategy"] = [
            "Optimize posting times for maximum reach",
            "Leverage cross-platform promotion",
            "Engage actively in comments and community",
            "Collaborate with other creators"
        ]
        
        return strategy
    
    def _identify_viral_success_patterns(self, viral_analysis: List[Dict[str, Any]]) -> List[str]:
        """Identify patterns in successful viral content."""
        high_performers = [v for v in viral_analysis if v["viral_score"] > 60]
        
        if not high_performers:
            return ["No clear viral success patterns identified yet"]
        
        patterns = []
        
        # Analyze common factors in high performers
        avg_engagement = statistics.mean([v["key_factors"]["engagement_velocity"] for v in high_performers])
        if avg_engagement > 60:
            patterns.append("High engagement velocity is a key success factor")
        
        avg_trending = statistics.mean([v["key_factors"]["trending_topic_alignment"] for v in high_performers])
        if avg_trending > 50:
            patterns.append("Trending topic alignment drives viral potential")
        
        return patterns if patterns else ["Emerging success patterns - continue monitoring"]
    
    def _estimate_market_position(self, category: str, performance: float, views: int) -> str:
        """Estimate market position within category."""
        # Simulate market position calculation
        if performance > 80 and views > 100000:
            return "market_leader"
        elif performance > 60 and views > 50000:
            return "strong_competitor"
        elif performance > 40 and views > 10000:
            return "emerging_player"
        else:
            return "developing"
    
    def _calculate_competitive_strength(self, category: str, data: Dict[str, Any]) -> float:
        """Calculate competitive strength score."""
        factors = {
            "content_volume": min(len(data["videos"]) / 10 * 100, 100),
            "performance_quality": data["avg_performance"],
            "audience_reach": min(data["total_views"] / 100000 * 100, 100),
            "consistency": 80 if len(data["videos"]) >= 5 else 40
        }
        
        return statistics.mean(list(factors.values()))
    
    def _assess_growth_opportunity(self, category: str, data: Dict[str, Any]) -> str:
        """Assess growth opportunity in category."""
        if data["avg_performance"] > 70:
            return "high_growth_potential"
        elif data["avg_performance"] > 50:
            return "moderate_growth_potential"
        else:
            return "improvement_needed"
    
    def _identify_market_opportunities_detailed(self, competitive_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify detailed market opportunities."""
        opportunities = []
        
        for category, data in competitive_analysis.items():
            if data["growth_opportunity"] == "high_growth_potential":
                opportunities.append({
                    "category": category,
                    "opportunity_type": "scale_success",
                    "description": f"Scale successful {category} content",
                    "potential": "high"
                })
            elif data["competitive_strength"] < 50:
                opportunities.append({
                    "category": category,
                    "opportunity_type": "market_entry",
                    "description": f"Establish stronger presence in {category}",
                    "potential": "medium"
                })
        
        return opportunities
    
    def _identify_competitive_advantages(self, videos: List[Dict[str, Any]], competitive_analysis: Dict[str, Any]) -> List[str]:
        """Identify competitive advantages."""
        advantages = []
        
        # Quality advantage
        avg_performance = statistics.mean([v.get("performance_score", 0) for v in videos])
        if avg_performance > 70:
            advantages.append("High content quality and production value")
        
        # Consistency advantage
        if len(videos) >= 10:
            advantages.append("Consistent content creation and publishing")
        
        # Niche expertise
        categories = [v.get("category", "unknown") for v in videos]
        if len(set(categories)) <= 2:
            advantages.append("Strong niche focus and expertise")
        
        return advantages if advantages else ["Opportunity to develop competitive advantages"]
    
    def _generate_competitive_strategy(self, competitive_analysis: Dict[str, Any]) -> List[str]:
        """Generate competitive strategy recommendations."""
        strategy = []
        
        # Find strongest category
        strongest_category = max(competitive_analysis.items(), key=lambda x: x[1]["competitive_strength"])
        strategy.append(f"Double down on {strongest_category[0]} content where you're strongest")
        
        # Find growth opportunities
        growth_categories = [cat for cat, data in competitive_analysis.items() if data["growth_opportunity"] == "high_growth_potential"]
        if growth_categories:
            strategy.append(f"Expand in high-growth categories: {', '.join(growth_categories)}")
        
        # Address weaknesses
        weak_categories = [cat for cat, data in competitive_analysis.items() if data["competitive_strength"] < 40]
        if weak_categories:
            strategy.append(f"Improve or consider pivoting from weak categories: {', '.join(weak_categories)}")
        
        return strategy
    
    def _get_duration_recommendation(self, correlation: float) -> str:
        """Get duration recommendation based on correlation analysis."""
        if correlation > 0.5:
            return "Longer content performs better - consider extending video length"
        elif correlation < -0.5:
            return "Shorter content performs better - consider reducing video length"
        else:
            return "Duration has minimal impact - focus on content quality over length"
    
    def _get_length_recommendation(self, best_group: str) -> str:
        """Get length recommendation based on best performing group."""
        recommendations = {
            "short": "Focus on short-form content (under 5 minutes) for optimal retention",
            "medium": "Medium-length content (5-15 minutes) works best for your audience",
            "long": "Long-form content (15+ minutes) shows strong retention - continue this approach"
        }
        return recommendations.get(best_group, "Continue testing different content lengths")
    
    def _identify_roi_optimization_opportunities(self, roi_metrics: List[Dict[str, Any]]) -> List[str]:
        """Identify ROI optimization opportunities."""
        opportunities = []
        
        # Low ROI content
        low_roi_count = len([m for m in roi_metrics if m["roi_percentage"] < 0])
        if low_roi_count > len(roi_metrics) * 0.3:
            opportunities.append("Reduce production costs or improve monetization for underperforming content")
        
        # High-cost, low-return content
        inefficient_content = [m for m in roi_metrics if m["efficiency_ratio"] < 1.0]
        if inefficient_content:
            opportunities.append("Optimize production workflow to reduce costs while maintaining quality")
        
        # Successful patterns to scale
        high_roi_content = [m for m in roi_metrics if m["roi_percentage"] > 100]
        if high_roi_content:
            opportunities.append("Scale successful content formats that show high ROI")
        
        # Revenue optimization
        avg_revenue = statistics.mean([m["revenue"] for m in roi_metrics])
        if avg_revenue < 50:
            opportunities.append("Implement additional monetization strategies to increase revenue per video")
        
        return opportunities if opportunities else ["Continue monitoring ROI metrics for optimization opportunities"]
    
    def _generate_lifecycle_recommendations(self, pattern: str, stage_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on lifecycle pattern."""
        recommendations = []
        
        if pattern == "improving":
            recommendations.extend([
                "Continue current growth trajectory",
                "Scale successful content strategies",
                "Invest in higher production quality",
                "Expand content variety while maintaining quality"
            ])
        elif pattern == "declining":
            recommendations.extend([
                "Analyze recent performance drops",
                "Refresh content strategy and formats",
                "Re-engage with audience through community building",
                "Consider pivoting to trending topics or formats"
            ])
        elif pattern == "stable":
            recommendations.extend([
                "Experiment with new content formats",
                "Optimize existing successful content",
                "Focus on audience growth strategies",
                "Consider seasonal content planning"
            ])
        else:
            recommendations.extend([
                "Create more content to establish patterns",
                "Focus on consistency in posting schedule",
                "Develop content strategy framework",
                "Monitor performance metrics closely"
            ])
        
        return recommendations
    
    def _predict_next_stage_performance(self, stage_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Predict next stage performance based on current trends."""
        if len(stage_analysis) < 2:
            return {"prediction": "insufficient_data"}
        
        # Get performance progression
        stages = ["launch", "growth", "maturity", "optimization"]
        available_stages = [stage for stage in stages if stage in stage_analysis]
        
        if len(available_stages) >= 2:
            recent_performance = stage_analysis[available_stages[-1]]["avg_performance"]
            previous_performance = stage_analysis[available_stages[-2]]["avg_performance"]
            
            trend = recent_performance - previous_performance
            next_predicted = max(0, min(100, recent_performance + trend))
            
            confidence = "high" if abs(trend) < 10 else "medium" if abs(trend) < 20 else "low"
            
            return {
                "predicted_performance": round(next_predicted, 1),
                "trend_direction": "improving" if trend > 0 else "declining" if trend < 0 else "stable",
                "confidence": confidence,
                "recommendation": "maintain_strategy" if trend >= 0 else "adjust_strategy"
            }
        
        return {"prediction": "insufficient_stage_data"}

class PerformancePredictor:
    """Advanced performance prediction engine."""
    
    def __init__(self):
        self.prediction_models = self._initialize_models()
    
    def _initialize_models(self) -> Dict[str, Any]:
        """Initialize prediction models and parameters."""
        return {
            "engagement_model": {
                "factors": ["title_quality", "thumbnail_appeal", "topic_relevance", "posting_time"],
                "weights": [0.3, 0.25, 0.25, 0.2]
            },
            "growth_model": {
                "factors": ["content_consistency", "audience_retention", "engagement_rate", "market_trends"],
                "weights": [0.35, 0.25, 0.25, 0.15]
            },
            "revenue_model": {
                "factors": ["view_count", "audience_demographics", "content_category", "monetization_strategy"],
                "weights": [0.4, 0.2, 0.2, 0.2]
            }
        }
    
    def predict_video_performance(self, video_data: Dict[str, Any], historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict individual video performance based on characteristics and historical data."""
        try:
            if not historical_data:
                return {"error": "No historical data available for prediction"}
            
            # Extract features from video data
            features = self._extract_video_features(video_data)
            
            # Calculate baseline performance from historical data
            baseline_performance = statistics.mean([v.get("performance_score", 0) for v in historical_data])
            
            # Apply feature-based adjustments
            performance_adjustments = self._calculate_performance_adjustments(features, historical_data)
            
            # Predict performance metrics
            predicted_performance = max(0, min(100, baseline_performance + performance_adjustments["total_adjustment"]))
            
            # Predict specific metrics
            avg_views = statistics.mean([v.get("views", 0) for v in historical_data])
            predicted_views = int(avg_views * (predicted_performance / baseline_performance)) if baseline_performance > 0 else avg_views
            
            # Calculate confidence intervals
            confidence_intervals = self._calculate_confidence_intervals(predicted_performance, historical_data)
            
            return {
                "predicted_performance_score": round(predicted_performance, 1),
                "predicted_views": predicted_views,
                "confidence_intervals": confidence_intervals,
                "key_factors": performance_adjustments["factor_impacts"],
                "prediction_confidence": self._assess_prediction_confidence(historical_data),
                "optimization_suggestions": self._generate_optimization_suggestions(features, performance_adjustments)
            }
            
        except Exception as e:
            logger.error(f"Error predicting video performance: {str(e)}")
            return {"error": str(e)}
    
    def predict_channel_growth(self, current_metrics: Dict[str, Any], historical_data: List[Dict[str, Any]], timeframe_months: int = 6) -> Dict[str, Any]:
        """Predict channel growth over specified timeframe."""
        try:
            if len(historical_data) < 3:
                return {"error": "Insufficient historical data for growth prediction"}
            
            # Calculate current growth rates
            growth_rates = self._calculate_growth_rates(historical_data)
            
            # Project future metrics
            projections = {}
            for metric, rate in growth_rates.items():
                current_value = current_metrics.get(metric, 0)
                projected_value = current_value * ((1 + rate) ** timeframe_months)
                projections[metric] = {
                    "current": current_value,
                    "projected": round(projected_value, 2),
                    "growth_rate": round(rate * 100, 2),
                    "absolute_growth": round(projected_value - current_value, 2)
                }
            
            # Calculate milestone predictions
            milestones = self._predict_growth_milestones(current_metrics, growth_rates)
            
            # Assess growth sustainability
            sustainability = self._assess_growth_sustainability(growth_rates, historical_data)
            
            return {
                "timeframe_months": timeframe_months,
                "growth_projections": projections,
                "milestone_predictions": milestones,
                "growth_sustainability": sustainability,
                "key_growth_drivers": self._identify_growth_drivers(historical_data),
                "growth_optimization_strategy": self._create_growth_strategy(growth_rates, current_metrics)
            }
            
        except Exception as e:
            logger.error(f"Error predicting channel growth: {str(e)}")
            return {"error": str(e)}
    
    def predict_revenue_potential(self, content_plan: List[Dict[str, Any]], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict revenue potential based on content plan and market conditions."""
        try:
            revenue_predictions = []
            total_predicted_revenue = 0
            
            for content_item in content_plan:
                # Predict individual content revenue
                item_prediction = self._predict_content_revenue(content_item, market_data)
                revenue_predictions.append(item_prediction)
                total_predicted_revenue += item_prediction["predicted_revenue"]
            
            # Calculate revenue streams breakdown
            revenue_streams = self._analyze_revenue_streams(revenue_predictions)
            
            # Assess market opportunities
            market_opportunities = self._assess_market_revenue_opportunities(market_data)
            
            # Calculate ROI projections
            roi_projections = self._calculate_roi_projections(revenue_predictions, content_plan)
            
            return {
                "total_predicted_revenue": round(total_predicted_revenue, 2),
                "individual_predictions": revenue_predictions,
                "revenue_streams_breakdown": revenue_streams,
                "market_opportunities": market_opportunities,
                "roi_projections": roi_projections,
                "revenue_optimization_tips": self._generate_revenue_optimization_tips(revenue_predictions),
                "risk_assessment": self._assess_revenue_risks(revenue_predictions, market_data)
            }
            
        except Exception as e:
            logger.error(f"Error predicting revenue potential: {str(e)}")
            return {"error": str(e)}
    
    # Helper methods for PerformancePredictor
    def _extract_video_features(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract predictive features from video data."""
        features = {
            "title_length": len(video_data.get("title", "")),
            "title_keywords": self._count_power_keywords(video_data.get("title", "")),
            "category": video_data.get("category", "unknown"),
            "estimated_duration": video_data.get("duration", 600),
            "has_thumbnail": bool(video_data.get("thumbnail_path")),
            "topic_trending_score": self._assess_topic_trending(video_data.get("title", ""))
        }
        return features
    
    def _calculate_performance_adjustments(self, features: Dict[str, Any], historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate performance adjustments based on features."""
        adjustments = {
            "title_impact": 0,
            "category_impact": 0,
            "duration_impact": 0,
            "trending_impact": 0
        }
        
        # Title impact
        if features["title_keywords"] > 2:
            adjustments["title_impact"] = 5
        elif features["title_keywords"] > 0:
            adjustments["title_impact"] = 2
        
        # Category impact (based on historical performance)
        category_performance = self._get_category_performance(features["category"], historical_data)
        adjustments["category_impact"] = category_performance - 50  # Adjust from baseline
        
        # Duration impact
        optimal_duration = self._get_optimal_duration(historical_data)
        duration_diff = abs(features["estimated_duration"] - optimal_duration)
        adjustments["duration_impact"] = max(-10, -duration_diff / 60)  # Penalty for deviation
        
        # Trending topic impact
        adjustments["trending_impact"] = features["topic_trending_score"] / 10
        
        total_adjustment = sum(adjustments.values())
        
        return {
            "factor_impacts": adjustments,
            "total_adjustment": total_adjustment
        }
    
    def _calculate_confidence_intervals(self, predicted_performance: float, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate confidence intervals for predictions."""
        historical_scores = [v.get("performance_score", 0) for v in historical_data]
        std_dev = statistics.stdev(historical_scores) if len(historical_scores) > 1 else 10
        
        return {
            "lower_bound": max(0, round(predicted_performance - 1.96 * std_dev, 1)),
            "upper_bound": min(100, round(predicted_performance + 1.96 * std_dev, 1)),
            "confidence_level": 95
        }
    
    def _assess_prediction_confidence(self, historical_data: List[Dict[str, Any]]) -> str:
        """Assess confidence level of predictions."""
        data_points = len(historical_data)
        
        if data_points >= 20:
            return "high"
        elif data_points >= 10:
            return "medium"
        elif data_points >= 5:
            return "low"
        else:
            return "very_low"
    
    def _generate_optimization_suggestions(self, features: Dict[str, Any], adjustments: Dict[str, Any]) -> List[str]:
        """Generate optimization suggestions based on prediction factors."""
        suggestions = []
        
        if adjustments["factor_impacts"]["title_impact"] < 2:
            suggestions.append("Optimize title with more engaging keywords")
        
        if adjustments["factor_impacts"]["trending_impact"] < 3:
            suggestions.append("Incorporate trending topics or keywords")
        
        if adjustments["factor_impacts"]["duration_impact"] < -5:
            suggestions.append("Adjust video duration closer to optimal length")
        
        if not suggestions:
            suggestions.append("Content shows strong optimization - maintain current approach")
        
        return suggestions
    
    def _calculate_growth_rates(self, historical_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate growth rates for various metrics."""
        if len(historical_data) < 2:
            return {}
        
        # Sort by date
        sorted_data = sorted(historical_data, key=lambda x: x.get("created_at", ""))
        
        growth_rates = {}
        metrics = ["views", "subscribers", "engagement_score", "revenue_total"]
        
        for metric in metrics:
            values = [v.get(metric, 0) for v in sorted_data if v.get(metric, 0) > 0]
            if len(values) >= 2:
                # Calculate compound monthly growth rate
                periods = len(values) - 1
                if values[0] > 0:
                    growth_rate = (values[-1] / values[0]) ** (1/periods) - 1
                    growth_rates[metric] = growth_rate
        
        return growth_rates
    
    def _predict_growth_milestones(self, current_metrics: Dict[str, Any], growth_rates: Dict[str, float]) -> List[Dict[str, Any]]:
        """Predict when growth milestones will be reached."""
        milestones = []
        
        # Subscriber milestones
        current_subs = current_metrics.get("subscribers", 0)
        sub_growth_rate = growth_rates.get("subscribers", 0.05)  # Default 5% monthly
        
        sub_milestones = [1000, 10000, 100000, 1000000]
        for milestone in sub_milestones:
            if current_subs < milestone and sub_growth_rate > 0:
                months_to_milestone = math.log(milestone / max(current_subs, 1)) / math.log(1 + sub_growth_rate)
                if months_to_milestone <= 24:  # Within 2 years
                    milestones.append({
                        "metric": "subscribers",
                        "milestone": milestone,
                        "estimated_months": round(months_to_milestone, 1),
                        "confidence": max(20, min(90, 80 - months_to_milestone * 2))  # Confidence decreases with time
                    })
        
        # View milestones
        current_views = current_metrics.get("total_views", 0)
        view_growth_rate = growth_rates.get("views", 0.08)  # Default 8% monthly
        
        view_milestones = [10000, 100000, 1000000, 10000000]
        for milestone in view_milestones:
            if current_views < milestone and view_growth_rate > 0:
                months_to_milestone = math.log(milestone / max(current_views, 1)) / math.log(1 + view_growth_rate)
                if months_to_milestone <= 18:  # Within 1.5 years
                    milestones.append({
                        "metric": "total_views",
                        "milestone": milestone,
                        "estimated_months": round(months_to_milestone, 1),
                        "confidence": max(25, min(85, 75 - months_to_milestone * 2))
                    })
        
        return sorted(milestones, key=lambda x: x["estimated_months"])[:5]  # Top 5 nearest milestones
    
    def _assess_growth_sustainability(self, growth_rates: Dict[str, float], historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess sustainability of current growth rates."""
        sustainability_factors = {
            "content_consistency": self._assess_content_consistency(historical_data),
            "engagement_stability": self._assess_engagement_stability(historical_data),
            "growth_rate_stability": self._assess_growth_rate_stability(growth_rates),
            "market_saturation_risk": self._assess_market_saturation_risk(growth_rates)
        }
        
        overall_sustainability = statistics.mean(list(sustainability_factors.values()))
        
        if overall_sustainability >= 80:
            sustainability_level = "high"
            outlook = "Growth trajectory is highly sustainable"
        elif overall_sustainability >= 60:
            sustainability_level = "medium"
            outlook = "Growth is moderately sustainable with some risks"
        elif overall_sustainability >= 40:
            sustainability_level = "low"
            outlook = "Growth sustainability faces significant challenges"
        else:
            sustainability_level = "at_risk"
            outlook = "Current growth rate is likely unsustainable"
        
        return {
            "sustainability_level": sustainability_level,
            "sustainability_score": round(overall_sustainability, 1),
            "outlook": outlook,
            "factors": {k: round(v, 1) for k, v in sustainability_factors.items()},
            "recommendations": self._generate_sustainability_recommendations(sustainability_factors)
        }
    
    def _identify_growth_drivers(self, historical_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify key factors driving growth."""
        drivers = []
        
        # Analyze content performance correlation
        if len(historical_data) >= 5:
            # Content quality driver
            performance_scores = [v.get("performance_score", 0) for v in historical_data]
            views = [v.get("views", 0) for v in historical_data]
            
            if len(performance_scores) == len(views) and len(views) > 1:
                correlation = self._calculate_correlation(performance_scores, views)
                if correlation > 0.5:
                    drivers.append({
                        "driver": "content_quality",
                        "impact": "high",
                        "correlation": round(correlation, 3),
                        "description": "High-quality content strongly drives view growth"
                    })
            
            # Consistency driver
            posting_consistency = self._calculate_posting_consistency(historical_data)
            if posting_consistency > 0.8:
                drivers.append({
                    "driver": "posting_consistency",
                    "impact": "medium",
                    "score": round(posting_consistency, 3),
                    "description": "Consistent posting schedule supports steady growth"
                })
            
            # Engagement driver
            engagement_scores = [v.get("engagement_score", 0) for v in historical_data]
            if engagement_scores and statistics.mean(engagement_scores) > 0.05:
                drivers.append({
                    "driver": "audience_engagement",
                    "impact": "high",
                    "avg_engagement": round(statistics.mean(engagement_scores), 4),
                    "description": "Strong audience engagement fuels organic growth"
                })
        
        return drivers if drivers else [{"driver": "insufficient_data", "description": "More data needed to identify growth drivers"}]
    
    def _create_growth_strategy(self, growth_rates: Dict[str, float], current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Create growth optimization strategy."""
        strategy = {
            "focus_areas": [],
            "optimization_tactics": [],
            "timeline": "3-6 months",
            "success_metrics": []
        }
        
        # Analyze current growth performance
        avg_growth_rate = statistics.mean(list(growth_rates.values())) if growth_rates else 0
        
        if avg_growth_rate > 0.1:  # >10% monthly growth
            strategy["focus_areas"].append("Scale successful strategies")
            strategy["optimization_tactics"].append("Increase content production frequency")
        elif avg_growth_rate > 0.05:  # 5-10% monthly growth
            strategy["focus_areas"].append("Optimize existing content performance")
            strategy["optimization_tactics"].append("Improve content quality and engagement")
        else:  # <5% monthly growth
            strategy["focus_areas"].append("Fundamental strategy revision needed")
            strategy["optimization_tactics"].append("Pivot content strategy and audience targeting")
        
        # Add specific tactics based on metrics
        if current_metrics.get("engagement_score", 0) < 0.03:
            strategy["optimization_tactics"].append("Focus on community building and engagement")
        
        if current_metrics.get("subscribers", 0) < 1000:
            strategy["optimization_tactics"].append("Implement subscriber acquisition campaigns")
        
        # Define success metrics
        strategy["success_metrics"] = [
            f"Achieve {max(5, avg_growth_rate * 100 * 1.5):.1f}% monthly growth rate",
            "Improve engagement rate by 25%",
            "Increase content consistency to 90%+"
        ]
        
        return strategy
    
    def _predict_content_revenue(self, content_item: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict revenue for individual content item."""
        # Estimate views based on content characteristics
        base_views = market_data.get("average_views", 5000)
        category_multiplier = market_data.get("category_multipliers", {}).get(content_item.get("category", "general"), 1.0)
        estimated_views = int(base_views * category_multiplier)
        
        # Calculate revenue streams
        ad_revenue = estimated_views * 0.003  # $3 per 1000 views
        sponsorship_revenue = ad_revenue * 0.5 if estimated_views > 10000 else 0
        affiliate_revenue = ad_revenue * 0.3 if content_item.get("has_affiliate_potential", False) else 0
        
        total_revenue = ad_revenue + sponsorship_revenue + affiliate_revenue
        
        return {
            "content_title": content_item.get("title", "Unknown"),
            "estimated_views": estimated_views,
            "predicted_revenue": round(total_revenue, 2),
            "revenue_breakdown": {
                "ad_revenue": round(ad_revenue, 2),
                "sponsorship_revenue": round(sponsorship_revenue, 2),
                "affiliate_revenue": round(affiliate_revenue, 2)
            },
            "confidence": self._assess_content_revenue_confidence(content_item, market_data)
        }
    
    def _analyze_revenue_streams(self, revenue_predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze revenue streams breakdown."""
        total_ad = sum(p["revenue_breakdown"]["ad_revenue"] for p in revenue_predictions)
        total_sponsorship = sum(p["revenue_breakdown"]["sponsorship_revenue"] for p in revenue_predictions)
        total_affiliate = sum(p["revenue_breakdown"]["affiliate_revenue"] for p in revenue_predictions)
        total_revenue = total_ad + total_sponsorship + total_affiliate
        
        return {
            "ad_revenue": {
                "amount": round(total_ad, 2),
                "percentage": round(total_ad / total_revenue * 100, 1) if total_revenue > 0 else 0
            },
            "sponsorship_revenue": {
                "amount": round(total_sponsorship, 2),
                "percentage": round(total_sponsorship / total_revenue * 100, 1) if total_revenue > 0 else 0
            },
            "affiliate_revenue": {
                "amount": round(total_affiliate, 2),
                "percentage": round(total_affiliate / total_revenue * 100, 1) if total_revenue > 0 else 0
            },
            "diversification_score": self._calculate_revenue_diversification(total_ad, total_sponsorship, total_affiliate)
        }
    
    def _assess_market_revenue_opportunities(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Assess market opportunities for revenue growth."""
        opportunities = []
        
        # High-value categories
        category_multipliers = market_data.get("category_multipliers", {})
        high_value_categories = [cat for cat, mult in category_multipliers.items() if mult > 1.5]
        
        if high_value_categories:
            opportunities.append({
                "opportunity": "high_value_categories",
                "description": f"Expand into high-revenue categories: {', '.join(high_value_categories)}",
                "potential_impact": "high",
                "implementation_difficulty": "medium"
            })
        
        # Sponsorship opportunities
        avg_views = market_data.get("average_views", 0)
        if avg_views > 10000:
            opportunities.append({
                "opportunity": "sponsorship_deals",
                "description": "Leverage view count for sponsorship opportunities",
                "potential_impact": "high",
                "implementation_difficulty": "low"
            })
        
        # Affiliate marketing
        opportunities.append({
            "opportunity": "affiliate_marketing",
            "description": "Implement strategic affiliate marketing programs",
            "potential_impact": "medium",
            "implementation_difficulty": "low"
        })
        
        return opportunities
    
    def _calculate_roi_projections(self, revenue_predictions: List[Dict[str, Any]], content_plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate ROI projections for content plan."""
        total_revenue = sum(p["predicted_revenue"] for p in revenue_predictions)
        
        # Estimate total investment
        total_investment = 0
        for content_item in content_plan:
            duration = content_item.get("duration", 600)
            category = content_item.get("category", "general")
            investment = self._estimate_content_investment(duration, category)
            total_investment += investment
        
        roi_percentage = ((total_revenue - total_investment) / total_investment * 100) if total_investment > 0 else 0
        payback_period = (total_investment / (total_revenue / len(content_plan))) if total_revenue > 0 else float('inf')
        
        return {
            "total_investment": round(total_investment, 2),
            "total_predicted_revenue": round(total_revenue, 2),
            "net_profit": round(total_revenue - total_investment, 2),
            "roi_percentage": round(roi_percentage, 1),
            "payback_period_months": round(payback_period, 1) if payback_period != float('inf') else "N/A",
            "break_even_views": int(total_investment / 0.003) if total_investment > 0 else 0
        }
    
    # Additional helper methods
    def _count_power_keywords(self, title: str) -> int:
        """Count power keywords in title."""
        power_keywords = [
            "how to", "tutorial", "guide", "tips", "secrets", "ultimate", "best", "top",
            "review", "vs", "comparison", "new", "2024", "beginner", "advanced", "free"
        ]
        title_lower = title.lower()
        return sum(1 for keyword in power_keywords if keyword in title_lower)
    
    def _assess_topic_trending(self, title: str) -> float:
        """Assess how trending the topic is (0-100 score)."""
        # Simulate trending topic assessment
        trending_terms = ["ai", "crypto", "nft", "metaverse", "web3", "sustainability", "remote work"]
        title_lower = title.lower()
        score = sum(20 for term in trending_terms if term in title_lower)
        return min(100, score)
    
    def _get_category_performance(self, category: str, historical_data: List[Dict[str, Any]]) -> float:
        """Get average performance for category from historical data."""
        category_videos = [v for v in historical_data if v.get("category") == category]
        if category_videos:
            return statistics.mean([v.get("performance_score", 50) for v in category_videos])
        return 50  # Default baseline
    
    def _get_optimal_duration(self, historical_data: List[Dict[str, Any]]) -> int:
        """Get optimal duration based on historical performance."""
        if not historical_data:
            return 600  # Default 10 minutes
        
        # Find duration that correlates with highest performance
        duration_performance = [(v.get("duration", 600), v.get("performance_score", 0)) for v in historical_data]
        if duration_performance:
            # Sort by performance and get median duration of top performers
            top_performers = sorted(duration_performance, key=lambda x: x[1], reverse=True)[:len(duration_performance)//3]
            optimal_duration = statistics.median([dp[0] for dp in top_performers])
            return int(optimal_duration)
        
        return 600
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate correlation coefficient between two lists."""
        if len(x) != len(y) or len(x) < 2:
            return 0
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(xi ** 2 for xi in x)
        sum_y2 = sum(yi ** 2 for yi in y)
        
        denominator = math.sqrt((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2))
        if denominator == 0:
            return 0
        
        return (n * sum_xy - sum_x * sum_y) / denominator
    
    def _calculate_posting_consistency(self, historical_data: List[Dict[str, Any]]) -> float:
        """Calculate posting consistency score."""
        if len(historical_data) < 3:
            return 0.5
        
        # Analyze posting intervals
        dates = [v.get("created_at", "") for v in historical_data if v.get("created_at")]
        if len(dates) < 3:
            return 0.5
        
        # Convert to datetime and calculate intervals
        try:
            sorted_dates = sorted([datetime.fromisoformat(d.replace('Z', '+00:00')) for d in dates])
            intervals = [(sorted_dates[i+1] - sorted_dates[i]).days for i in range(len(sorted_dates)-1)]
            
            if not intervals:
                return 0.5
            
            # Calculate consistency based on standard deviation of intervals
            mean_interval = statistics.mean(intervals)
            if len(intervals) > 1:
                std_dev = statistics.stdev(intervals)
                consistency = max(0, 1 - (std_dev / mean_interval)) if mean_interval > 0 else 0.5
            else:
                consistency = 0.8  # Single interval, assume good consistency
            
            return min(1.0, consistency)
        except:
            return 0.5
    
    def _assess_content_consistency(self, historical_data: List[Dict[str, Any]]) -> float:
        """Assess content consistency factor for sustainability."""
        posting_consistency = self._calculate_posting_consistency(historical_data)
        
        # Quality consistency
        performance_scores = [v.get("performance_score", 0) for v in historical_data]
        if len(performance_scores) > 1:
            quality_consistency = 100 - (statistics.stdev(performance_scores) / statistics.mean(performance_scores) * 100) if statistics.mean(performance_scores) > 0 else 50
        else:
            quality_consistency = 70
        
        return (posting_consistency * 100 + max(0, min(100, quality_consistency))) / 2
    
    def _assess_engagement_stability(self, historical_data: List[Dict[str, Any]]) -> float:
        """Assess engagement stability for sustainability."""
        engagement_scores = [v.get("engagement_score", 0) for v in historical_data]
        if len(engagement_scores) < 2:
            return 60
        
        mean_engagement = statistics.mean(engagement_scores)
        if mean_engagement == 0:
            return 30
        
        # Calculate coefficient of variation
        std_dev = statistics.stdev(engagement_scores)
        cv = std_dev / mean_engagement
        
        # Convert to stability score (lower CV = higher stability)
        stability = max(0, 100 - (cv * 100))
        return min(100, stability)
    
    def _assess_growth_rate_stability(self, growth_rates: Dict[str, float]) -> float:
        """Assess growth rate stability."""
        if not growth_rates:
            return 40
        
        rates = list(growth_rates.values())
        if len(rates) == 1:
            return 70 if rates[0] > 0 else 30
        
        # Check for consistent positive growth
        positive_rates = [r for r in rates if r > 0]
        consistency_score = (len(positive_rates) / len(rates)) * 100
        
        # Check for reasonable growth rates (not too volatile)
        if len(rates) > 1:
            rate_std = statistics.stdev(rates)
            rate_mean = statistics.mean(rates)
            if rate_mean > 0:
                volatility_penalty = min(30, (rate_std / rate_mean) * 50)
                consistency_score -= volatility_penalty
        
        return max(0, min(100, consistency_score))
    
    def _assess_market_saturation_risk(self, growth_rates: Dict[str, float]) -> float:
        """Assess market saturation risk."""
        # Simulate market saturation assessment
        avg_growth = statistics.mean(list(growth_rates.values())) if growth_rates else 0
        
        if avg_growth > 0.2:  # >20% monthly growth
            return 60  # High growth may indicate approaching saturation
        elif avg_growth > 0.1:  # 10-20% monthly growth
            return 80  # Sustainable growth range
        elif avg_growth > 0.05:  # 5-10% monthly growth
            return 85  # Stable growth
        else:
            return 70  # Low growth, but also low saturation risk
    
    def _generate_sustainability_recommendations(self, factors: Dict[str, float]) -> List[str]:
        """Generate sustainability recommendations."""
        recommendations = []
        
        if factors["content_consistency"] < 70:
            recommendations.append("Improve content posting consistency and quality standards")
        
        if factors["engagement_stability"] < 60:
            recommendations.append("Focus on building stable audience engagement through community interaction")
        
        if factors["growth_rate_stability"] < 60:
            recommendations.append("Develop more predictable growth strategies to reduce volatility")
        
        if factors["market_saturation_risk"] < 70:
            recommendations.append("Diversify content strategy to mitigate market saturation risks")
        
        if not recommendations:
            recommendations.append("Maintain current sustainable growth approach")
        
        return recommendations
    
    def _generate_revenue_optimization_tips(self, revenue_predictions: List[Dict[str, Any]]) -> List[str]:
        """Generate revenue optimization tips."""
        tips = []
        
        # Analyze revenue distribution
        total_revenue = sum(p["predicted_revenue"] for p in revenue_predictions)
        avg_revenue = total_revenue / len(revenue_predictions) if revenue_predictions else 0
        
        # Check for low-performing content
        low_performers = [p for p in revenue_predictions if p["predicted_revenue"] < avg_revenue * 0.5]
        if len(low_performers) > len(revenue_predictions) * 0.3:
            tips.append("Optimize or replace low-performing content to improve overall revenue")
        
        # Check revenue stream diversification
        ad_revenue_total = sum(p["revenue_breakdown"]["ad_revenue"] for p in revenue_predictions)
        if ad_revenue_total / total_revenue > 0.8 if total_revenue > 0 else True:
            tips.append("Diversify revenue streams beyond ad revenue (sponsorships, affiliates, products)")
        
        # High-value content opportunities
        high_performers = [p for p in revenue_predictions if p["predicted_revenue"] > avg_revenue * 1.5]
        if high_performers:
            tips.append("Scale successful high-revenue content formats and topics")
        
        if not tips:
            tips.append("Revenue optimization strategy is well-balanced")
        
        return tips
    
    def _assess_revenue_risks(self, revenue_predictions: List[Dict[str, Any]], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess revenue prediction risks."""
        risks = {
            "market_volatility": "medium",
            "platform_dependency": "high",
            "content_performance_variance": "medium",
            "monetization_policy_changes": "medium"
        }
        
        # Assess content performance variance risk
        revenues = [p["predicted_revenue"] for p in revenue_predictions]
        if len(revenues) > 1:
            cv = statistics.stdev(revenues) / statistics.mean(revenues) if statistics.mean(revenues) > 0 else 1
            if cv > 0.5:
                risks["content_performance_variance"] = "high"
            elif cv < 0.2:
                risks["content_performance_variance"] = "low"
        
        # Assess platform dependency
        ad_revenue_ratio = sum(p["revenue_breakdown"]["ad_revenue"] for p in revenue_predictions) / sum(p["predicted_revenue"] for p in revenue_predictions) if revenue_predictions else 1
        if ad_revenue_ratio > 0.8:
            risks["platform_dependency"] = "very_high"
        elif ad_revenue_ratio < 0.5:
            risks["platform_dependency"] = "medium"
        
        risk_score = {
            "very_high": 5,
            "high": 4,
            "medium": 3,
            "low": 2,
            "very_low": 1
        }
        
        overall_risk_score = statistics.mean([risk_score[risk] for risk in risks.values()])
        overall_risk = next(level for level, score in risk_score.items() if score >= overall_risk_score)
        
        return {
            "overall_risk": overall_risk,
            "risk_factors": risks,
            "risk_mitigation_strategies": self._generate_risk_mitigation_strategies(risks)
        }
    
    def _generate_risk_mitigation_strategies(self, risks: Dict[str, str]) -> List[str]:
        """Generate risk mitigation strategies."""
        strategies = []
        
        if risks["platform_dependency"] in ["high", "very_high"]:
            strategies.append("Diversify revenue streams and reduce platform dependency")
        
        if risks["content_performance_variance"] == "high":
            strategies.append("Develop more consistent content quality and performance standards")
        
        if risks["market_volatility"] in ["high", "very_high"]:
            strategies.append("Build audience loyalty and community to weather market changes")
        
        strategies.append("Maintain emergency fund equivalent to 3-6 months of expenses")
        strategies.append("Regularly review and adjust monetization strategies")
        
        return strategies
    
    def _assess_content_revenue_confidence(self, content_item: Dict[str, Any], market_data: Dict[str, Any]) -> str:
        """Assess confidence in content revenue prediction."""
        confidence_factors = []
        
        # Category data availability
        category = content_item.get("category", "unknown")
        if category in market_data.get("category_multipliers", {}):
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.4)
        
        # Content characteristics completeness
        if content_item.get("title") and content_item.get("duration"):
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.5)
        
        # Market data quality
        if market_data.get("average_views", 0) > 0:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.3)
        
        avg_confidence = statistics.mean(confidence_factors)
        
        if avg_confidence >= 0.8:
            return "high"
        elif avg_confidence >= 0.6:
            return "medium"
        else:
            return "low"
    
    def _calculate_revenue_diversification(self, ad_revenue: float, sponsorship_revenue: float, affiliate_revenue: float) -> float:
        """Calculate revenue diversification score."""
        total = ad_revenue + sponsorship_revenue + affiliate_revenue
        if total == 0:
            return 0
        
        # Calculate Herfindahl-Hirschman Index for diversification
        ad_share = ad_revenue / total
        sponsor_share = sponsorship_revenue / total
        affiliate_share = affiliate_revenue / total
        
        hhi = ad_share**2 + sponsor_share**2 + affiliate_share**2
        diversification_score = (1 - hhi) * 100  # Convert to 0-100 scale
        
        return round(diversification_score, 1)
    
    def _estimate_content_investment(self, duration: int, category: str) -> float:
        """Estimate investment required for content creation."""
        base_cost_per_minute = {
            "tech": 15.0,
            "gaming": 8.0,
            "education": 12.0,
            "entertainment": 20.0,
            "lifestyle": 10.0,
            "business": 18.0,
            "tutorial": 14.0
        }.get(category, 12.0)
        
        duration_minutes = duration / 60
        production_cost = base_cost_per_minute * duration_minutes
        
        # Add fixed costs
        equipment_amortization = 25  # Per video
        editing_time_cost = duration_minutes * 2  # 2x duration for editing
        
        total_investment = production_cost + equipment_amortization + editing_time_cost
        return round(total_investment, 2)

# Export the helper classes
__all__ = ['AdvancedAnalyticsHelper', 'PerformancePredictor']
