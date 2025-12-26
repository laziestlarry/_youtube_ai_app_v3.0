import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import APIRouter, HTTPException, BackgroundTasks
import structlog

from .database_manager import DatabaseManager
from .analytics_engine import AdvancedAnalyticsEngine

logger = structlog.get_logger()

class MonetizationTracker:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.analytics_engine = AdvancedAnalyticsEngine()
        self.revenue_streams = {
            "ad_revenue": {"weight": 0.4, "cpm_range": (1.0, 5.0)},
            "sponsorship": {"weight": 0.3, "rate_range": (100.0, 5000.0)},
            "affiliate": {"weight": 0.2, "commission_range": (0.05, 0.15)},
            "course_sales": {"weight": 0.1, "price_range": (50.0, 500.0)}
        }
    
    async def calculate_video_earnings(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive earnings for a video."""
        try:
            views = video_data.get("views", 0)
            engagement_rate = video_data.get("engagement_rate", 0.0)
            duration = video_data.get("duration", 0)  # in seconds
            category = video_data.get("category", "general")
            
            # Base CPM calculation based on category and engagement
            base_cpm = self._calculate_dynamic_cpm(category, engagement_rate, duration)
            
            # Ad Revenue Calculation
            ad_revenue = self._calculate_ad_revenue(views, base_cpm, duration)
            
            # Sponsorship Revenue (based on views and engagement)
            sponsorship_revenue = self._calculate_sponsorship_revenue(views, engagement_rate, category)
            
            # Affiliate Revenue (based on clicks and conversions)
            affiliate_revenue = self._calculate_affiliate_revenue(views, engagement_rate)
            
            # Course Sales Revenue (for educational content)
            course_revenue = self._calculate_course_revenue(views, engagement_rate, category)
            
            # Total Revenue
            total_revenue = ad_revenue + sponsorship_revenue + affiliate_revenue + course_revenue
            
            # Revenue Per Mille (RPM)
            rpm = (total_revenue / views * 1000) if views > 0 else 0
            
            earnings_data = {
                "video_id": video_data.get("id"),
                "views": views,
                "engagement_rate": engagement_rate,
                "revenue_breakdown": {
                    "ad_revenue": round(ad_revenue, 2),
                    "sponsorship_revenue": round(sponsorship_revenue, 2),
                    "affiliate_revenue": round(affiliate_revenue, 2),
                    "course_revenue": round(course_revenue, 2)
                },
                "total_revenue": round(total_revenue, 2),
                "cpm": round(base_cpm, 2),
                "rpm": round(rpm, 2),
                "calculated_at": datetime.utcnow().isoformat()
            }
            
            # Save to database
            await self.db_manager.save_monetization_record({
                "video_id": video_data.get("id"),
                "ad_revenue": ad_revenue,
                "sponsorship_revenue": sponsorship_revenue,
                "affiliate_revenue": affiliate_revenue,
                "total_revenue": total_revenue,
                "cpm": base_cpm,
                "rpm": rpm
            })
            
            logger.info("Video earnings calculated", video_id=video_data.get("id"), total_revenue=total_revenue)
            return earnings_data
            
        except Exception as e:
            logger.error("Failed to calculate video earnings", error=str(e))
            raise
    
    def _calculate_dynamic_cpm(self, category: str, engagement_rate: float, duration: int) -> float:
        """Calculate dynamic CPM based on multiple factors."""
        # Base CPM by category
        category_cpm = {
            "ai_monetization": 4.5,
            "entrepreneurship": 4.0,
            "finance": 5.0,
            "technology": 3.5,
            "education": 3.0,
            "general": 2.5
        }
        
        base_cpm = category_cpm.get(category, 2.5)
        
        # Engagement multiplier (higher engagement = higher CPM)
        engagement_multiplier = 1 + (engagement_rate / 100) * 0.5
        
        # Duration multiplier (longer videos typically have higher CPM)
        duration_multiplier = 1.0
        if duration > 600:  # 10+ minutes
            duration_multiplier = 1.3
        elif duration > 300:  # 5+ minutes
            duration_multiplier = 1.1
        
        # Time-based multiplier (seasonal adjustments)
        time_multiplier = self._get_seasonal_multiplier()
        
        final_cpm = base_cpm * engagement_multiplier * duration_multiplier * time_multiplier
        return min(final_cpm, 8.0)  # Cap at $8 CPM
    
    def _calculate_ad_revenue(self, views: int, cpm: float, duration: int) -> float:
        """Calculate ad revenue based on views, CPM, and video duration."""
        # Ad viewability rate (not all views generate ad revenue)
        viewability_rate = 0.85
        
        # Multiple ad placements for longer videos
        ad_placements = 1
        if duration > 480:  # 8+ minutes
            ad_placements = 2
        if duration > 900:  # 15+ minutes
            ad_placements = 3
        
        ad_views = views * viewability_rate * ad_placements
        return (ad_views / 1000) * cpm
    
    def _calculate_sponsorship_revenue(self, views: int, engagement_rate: float, category: str) -> float:
        """Calculate potential sponsorship revenue."""
        # Sponsorship rates by category (per 1000 views)
        sponsorship_rates = {
            "ai_monetization": 15.0,
            "entrepreneurship": 12.0,
            "finance": 18.0,
            "technology": 10.0,
            "education": 8.0,
            "general": 5.0
        }
        
        base_rate = sponsorship_rates.get(category, 5.0)
        
        # Engagement bonus
        engagement_bonus = 1 + (engagement_rate / 100) * 0.3
        
        # Only apply sponsorship revenue if views > 10,000
        if views < 10000:
            return 0.0
        
        return (views / 1000) * base_rate * engagement_bonus * 0.3  # 30% chance of sponsorship
    
    def _calculate_affiliate_revenue(self, views: int, engagement_rate: float) -> float:
        """Calculate affiliate marketing revenue."""
        # Affiliate conversion rates
        click_through_rate = 0.02  # 2% of viewers click affiliate links
        conversion_rate = 0.05  # 5% of clicks convert to sales
        average_commission = 50.0  # Average commission per sale
        
        # Engagement affects click-through rate
        adjusted_ctr = click_through_rate * (1 + engagement_rate / 100)
        
        clicks = views * adjusted_ctr
        conversions = clicks * conversion_rate
        
        return conversions * average_commission
    
    def _calculate_course_revenue(self, views: int, engagement_rate: float, category: str) -> float:
        """Calculate revenue from course sales."""
        if category not in ["ai_monetization", "entrepreneurship", "education"]:
            return 0.0
        
        # Course conversion rates
        course_ctr = 0.005  # 0.5% of viewers interested in courses
        course_conversion = 0.1  # 10% of interested viewers buy
        average_course_price = 200.0
        
        # Engagement affects conversion
        adjusted_conversion = course_conversion * (1 + engagement_rate / 100)
        
        interested_viewers = views * course_ctr
        course_sales = interested_viewers * adjusted_conversion
        
        return course_sales * average_course_price
    
    def _get_seasonal_multiplier(self) -> float:
        """Get seasonal CPM multiplier."""
        current_month = datetime.now().month
        
        # Higher CPM during Q4 (holiday season)
        if current_month in [11, 12]:
            return 1.4
        # Lower CPM during summer
        elif current_month in [6, 7, 8]:
            return 0.9
        # Normal CPM
        else:
            return 1.0
    
    async def process_recent_earnings(self, days: int = 7) -> Dict[str, Any]:
        """Process earnings for recent videos."""
        try:
            # Get recent videos
            videos = await self.db_manager.get_video_analytics(days=days)
            
            total_processed = 0
            total_revenue = 0.0
            
            for video in videos:
                earnings = await self.calculate_video_earnings(video)
                total_revenue += earnings["total_revenue"]
                total_processed += 1
            
            result = {
                "period_days": days,
                "videos_processed": total_processed,
                "total_revenue": round(total_revenue, 2),
                "average_revenue_per_video": round(total_revenue / total_processed, 2) if total_processed > 0 else 0,
                "processed_at": datetime.utcnow().isoformat()
            }
            
            logger.info("Recent earnings processed", result=result)
            return result
            
        except Exception as e:
            logger.error("Failed to process recent earnings", error=str(e))
            raise
    
    async def get_revenue_forecast(self, days_ahead: int = 30) -> Dict[str, Any]:
        """Generate revenue forecast based on historical data."""
        try:
            # Get historical data
            historical_videos = await self.db_manager.get_video_analytics(days=90)
            
            if not historical_videos:
                return {"error": "Insufficient historical data"}
            
            # Calculate growth trends
            growth_rates = self._calculate_growth_trends(historical_videos)
            
            # Current metrics
            recent_videos = historical_videos[:30]  # Last 30 videos
            current_avg_views = sum(v.get("views", 0) for v in recent_videos) / len(recent_videos)
            current_avg_revenue = await self._get_average_revenue(recent_videos)
            
            # Forecast calculations
            projected_videos = days_ahead // 2  # Assuming 1 video every 2 days
            
            # Apply growth rate
            growth_multiplier = 1 + (growth_rates.get("views", 0) * (days_ahead / 30))
            projected_avg_views = current_avg_views * growth_multiplier
            projected_avg_revenue = current_avg_revenue * growth_multiplier
            
            forecast = {
                "forecast_period_days": days_ahead,
                "projected_videos": projected_videos,
                "projected_total_views": round(projected_avg_views * projected_videos),
                "projected_total_revenue": round(projected_avg_revenue * projected_videos, 2),
                "projected_monthly_revenue": round(projected_avg_revenue * projected_videos * (30 / days_ahead), 2),
                "growth_rate": round(growth_rates.get("views", 0) * 100, 2),
                "confidence_level": self._calculate_confidence_level(historical_videos),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return forecast
            
        except Exception as e:
            logger.error("Failed to generate revenue forecast", error=str(e))
            raise
    
    def _calculate_growth_trends(self, videos: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate growth trends from historical data."""
        if len(videos) < 10:
            return {"views": 0.0, "engagement": 0.0}
        
        # Sort by date
        sorted_videos = sorted(videos, key=lambda x: x.get("published_at", ""))
        
        # Calculate monthly growth rates
        monthly_views = []
        monthly_engagement = []
        
        for i in range(0, len(sorted_videos), 30):  # Group by ~30 videos (monthly)
            month_videos = sorted_videos[i:i+30]
            if len(month_videos) >= 10:  # Minimum videos for reliable data
                avg_views = sum(v.get("views", 0) for v in month_videos) / len(month_videos)
                avg_engagement = sum(v.get("engagement_rate", 0) for v in month_videos) / len(month_videos)
                monthly_views.append(avg_views)
                monthly_engagement.append(avg_engagement)
        
        # Calculate growth rates
        views_growth = 0.0
        engagement_growth = 0.0
        
        if len(monthly_views) >= 2:
            views_growth = (monthly_views[-1] - monthly_views[0]) / monthly_views[0] / len(monthly_views)
            engagement_growth = (monthly_engagement[-1] - monthly_engagement[0]) / monthly_engagement[0] / len(monthly_engagement)
        
        return {
            "views": views_growth,
            "engagement": engagement_growth
        }
    
    async def _get_average_revenue(self, videos: List[Dict[str, Any]]) -> float:
        """Calculate average revenue per video."""
        total_revenue = 0.0
        
        for video in videos:
            earnings = await self.calculate_video_earnings(video)
            total_revenue += earnings["total_revenue"]
        
        return total_revenue / len(videos) if videos else 0.0
    
    def _calculate_confidence_level(self, videos: List[Dict[str, Any]]) -> str:
        """Calculate confidence level for forecasts."""
        if len(videos) >= 90:
            return "High"
        elif len(videos) >= 30:
            return "Medium"
        else:
            return "Low"
    
    async def get_monetization_insights(self) -> Dict[str, Any]:
        """Get comprehensive monetization insights."""
        try:
            # Get data for different periods
            last_30_days = await self.db_manager.get_video_analytics(days=30)
            last_90_days = await self.db_manager.get_video_analytics(days=90)
            
            # Calculate insights
            insights = {
                "performance_summary": await self._calculate_performance_summary(last_30_days),
                "revenue_trends": await self._calculate_revenue_trends(last_90_days),
                "optimization_opportunities": await self._identify_optimization_opportunities(last_30_days),
                "benchmark_comparison": await self._compare_with_benchmarks(last_30_days),
                "recommendations": await self._generate_monetization_recommendations(last_30_days)
            }
            
            return insights
            
        except Exception as e:
            logger.error("Failed to get monetization insights", error=str(e))
            raise
    
    async def _calculate_performance_summary(self, videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate performance summary."""
        if not videos:
            return {}
        
        total_views = sum(v.get("views", 0) for v in videos)
        total_revenue = 0.0
        
        for video in videos:
            earnings = await self.calculate_video_earnings(video)
            total_revenue += earnings["total_revenue"]
        
        avg_cpm = (total_revenue / total_views * 1000) if total_views > 0 else 0
        
        return {
            "total_videos": len(videos),
            "total_views": total_views,
            "total_revenue": round(total_revenue, 2),
            "average_views_per_video": round(total_views / len(videos)),
            "average_revenue_per_video": round(total_revenue / len(videos), 2),
            "average_cpm": round(avg_cpm, 2),
            "top_performing_video": max(videos, key=lambda x: x.get("views", 0))["title"] if videos else None
        }
    
    async def _identify_optimization_opportunities(self, videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify monetization optimization opportunities."""
        opportunities = []
        
        if not videos:
            return opportunities
        
        # Analyze video performance patterns
        high_performers = [v for v in videos if v.get("views", 0) > 50000]
        low_performers = [v for v in videos if v.get("views", 0) < 10000]
        
        # Opportunity 1: Content category optimization
        if high_performers:
            top_categories = {}
            for video in high_performers:
                category = video.get("category", "general")
                top_categories[category] = top_categories.get(category, 0) + 1
            
            best_category = max(top_categories, key=top_categories.get)
            opportunities.append({
                "type": "content_focus",
                "title": "Focus on High-Performing Categories",
                "description": f"Your '{best_category}' content performs best. Consider creating more videos in this category.",
                "potential_impact": "20-30% revenue increase",
                "priority": "high"
            })
        
        # Opportunity 2: Video length optimization
        long_videos = [v for v in videos if v.get("duration", 0) > 600]
        if long_videos:
            avg_long_views = sum(v.get("views", 0) for v in long_videos) / len(long_videos)
            avg_short_views = sum(v.get("views", 0) for v in videos if v.get("duration", 0) <= 600) / max(1, len(videos) - len(long_videos))
            
            if avg_long_views > avg_short_views * 1.2:
                opportunities.append({
                    "type": "duration_optimization",
                    "title": "Create Longer Content",
                    "description": "Your longer videos (10+ minutes) get significantly more views and ad revenue.",
                    "potential_impact": "15-25% revenue increase",
                    "priority": "medium"
                })
        
        # Opportunity 3: Engagement optimization
        low_engagement = [v for v in videos if v.get("engagement_rate", 0) < 2.0]
        if len(low_engagement) > len(videos) * 0.3:
            opportunities.append({
                "type": "engagement_boost",
                "title": "Improve Audience Engagement",
                "description": "30%+ of your videos have low engagement. Focus on CTAs, questions, and interactive content.",
                "potential_impact": "10-20% revenue increase",
                "priority": "high"
            })
        
        return opportunities
    
    async def _generate_monetization_recommendations(self, videos: List[Dict[str, Any]]) -> List[str]:
        """Generate specific monetization recommendations."""
        recommendations = []
        
        if not videos:
            return ["Insufficient data for recommendations"]
        
        avg_views = sum(v.get("views", 0) for v in videos) / len(videos)
        avg_engagement = sum(v.get("engagement_rate", 0) for v in videos) / len(videos)
        
        # View-based recommendations
        if avg_views < 10000:
            recommendations.append("Focus on SEO optimization and thumbnail design to increase views")
            recommendations.append("Consider collaborations with other creators to expand reach")
        elif avg_views > 50000:
            recommendations.append("You're ready for premium sponsorship deals - reach out to brands directly")
            recommendations.append("Consider launching your own course or digital product")
        
        # Engagement-based recommendations
        if avg_engagement < 2.0:
            recommendations.append("Add more calls-to-action to boost engagement")
            recommendations.append("Create content that encourages comments and discussion")
        elif avg_engagement > 5.0:
            recommendations.append("Your high engagement makes you attractive to sponsors")
            recommendations.append("Consider affiliate marketing for relevant products")
        
        # Category-specific recommendations
        categories = [v.get("category") for v in videos]
        if "ai_monetization" in categories:
            recommendations.append("Create AI tool reviews with affiliate links")
            recommendations.append("Offer AI consulting services to your audience")
        
        return recommendations[:5]  # Return top 5 recommendations

# FastAPI Router
MonetizationRouter = APIRouter()

@MonetizationRouter.get("/earnings/{video_id}")
async def get_video_earnings(video_id: str):
    """Get earnings data for a specific video."""
    try:
        tracker = MonetizationTracker()
        
        # Get video data from database
        video_data = await tracker.db_manager.get_video_by_id(video_id)
        if not video_data:
            raise HTTPException(status_code=404, detail="Video not found")
        
        earnings = await tracker.calculate_video_earnings(video_data)
        return earnings
        
    except Exception as e:
        logger.error("Failed to get video earnings", video_id=video_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@MonetizationRouter.get("/forecast")
async def get_revenue_forecast(days_ahead: int = 30):
    """Get revenue forecast."""
    try:
        tracker = MonetizationTracker()
        forecast = await tracker.get_revenue_forecast(days_ahead)
        return forecast
        
    except Exception as e:
        logger.error("Failed to get revenue forecast", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@MonetizationRouter.get("/insights")
async def get_monetization_insights():
    """Get comprehensive monetization insights."""
    try:
        tracker = MonetizationTracker()
        insights = await tracker.get_monetization_insights()
        return insights
        
    except Exception as e:
        logger.error("Failed to get monetization insights", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@MonetizationRouter.post("/process-earnings")
async def process_earnings(background_tasks: BackgroundTasks, days: int = 7):
    """Process earnings for recent videos."""
    try:
        tracker = MonetizationTracker()
        
        # Process in background
        background_tasks.add_task(tracker.process_recent_earnings, days)
        
        return {
            "status": "started",
            "message": f"Processing earnings for last {days} days",
            "days": days
        }
        
    except Exception as e:
        logger.error("Failed to start earnings processing", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))