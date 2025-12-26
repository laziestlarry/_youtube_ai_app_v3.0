import asyncio
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import statistics
import json
from ..database import get_db_connection
from ..config.enhanced_settings import settings

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Performance metric data point."""
    timestamp: datetime
    metric_name: str
    value: float
    component: str
    tags: Dict[str, str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}

@dataclass
class PerformanceAnalysis:
    """Performance analysis results."""
    metric_name: str
    component: str
    time_period: str
    average: float
    min_value: float
    max_value: float
    median: float
    std_deviation: float
    trend: str  # 'improving', 'degrading', 'stable'
    anomalies: List[Dict[str, Any]]
    recommendations: List[str]

class PerformanceAnalytics:
    """Advanced performance analytics and monitoring."""
    
    def __init__(self, max_history_days: int = 30):
        self.max_history_days = max_history_days
        self.metrics_buffer = defaultdict(lambda: deque(maxlen=1000))
        self.analysis_cache = {}
        self.anomaly_threshold = 2.0  # Standard deviations for anomaly detection
        self.trend_window = 100  # Number of points for trend analysis
        
    async def record_metric(
        self,
        metric_name: str,
        value: float,
        component: str,
        tags: Optional[Dict[str, str]] = None
    ):
        """Record a performance metric."""
        try:
            metric = PerformanceMetric(
                timestamp=datetime.now(),
                metric_name=metric_name,
                value=value,
                component=component,
                tags=tags or {}
            )
            
            # Add to buffer
            buffer_key = f"{component}:{metric_name}"
            self.metrics_buffer[buffer_key].append(metric)
            
            # Store in database
            await self._store_metric_to_db(metric)
            
            # Clear cache for this metric
            cache_key = f"{component}:{metric_name}"
            if cache_key in self.analysis_cache:
                del self.analysis_cache[cache_key]
                
        except Exception as e:
            logger.error(f"Error recording metric {metric_name}: {str(e)}")
    
    async def _store_metric_to_db(self, metric: PerformanceMetric):
        """Store metric to database."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO performance_metrics 
                    (timestamp, metric_name, value, component, tags)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    metric.timestamp.isoformat(),
                    metric.metric_name,
                    metric.value,
                    metric.component,
                    json.dumps(metric.tags)
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error storing metric to database: {str(e)}")
    
    async def get_metrics_history(
        self,
        component: str,
        metric_name: str,
        hours: int = 24
    ) -> List[PerformanceMetric]:
        """Get historical metrics data."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT timestamp, metric_name, value, component, tags
                    FROM performance_metrics
                    WHERE component = ? AND metric_name = ? AND timestamp > ?
                    ORDER BY timestamp ASC
                """, (component, metric_name, cutoff_time.isoformat()))
                
                metrics = []
                for row in cursor.fetchall():
                    metrics.append(PerformanceMetric(
                        timestamp=datetime.fromisoformat(row[0]),
                        metric_name=row[1],
                        value=row[2],
                        component=row[3],
                        tags=json.loads(row[4]) if row[4] else {}
                    ))
                
                return metrics
                
        except Exception as e:
            logger.error(f"Error fetching metrics history: {str(e)}")
            return []
    
    async def analyze_performance(
        self,
        component: str,
        metric_name: str,
        hours: int = 24
    ) -> PerformanceAnalysis:
        """Analyze performance metrics and generate insights."""
        try:
            cache_key = f"{component}:{metric_name}:{hours}"
            
            # Check cache first
            if cache_key in self.analysis_cache:
                cached_analysis, cache_time = self.analysis_cache[cache_key]
                if datetime.now() - cache_time < timedelta(minutes=5):
                    return cached_analysis
            
            # Get historical data
            metrics = await self.get_metrics_history(component, metric_name, hours)
            
            if not metrics:
                return PerformanceAnalysis(
                    metric_name=metric_name,
                    component=component,
                    time_period=f"{hours}h",
                    average=0.0,
                    min_value=0.0,
                    max_value=0.0,
                    median=0.0,
                    std_deviation=0.0,
                    trend="unknown",
                    anomalies=[],
                    recommendations=["Insufficient data for analysis"]
                )
            
            values = [m.value for m in metrics]
            
            # Calculate basic statistics
            avg_value = statistics.mean(values)
            min_value = min(values)
            max_value = max(values)
            median_value = statistics.median(values)
            std_dev = statistics.stdev(values) if len(values) > 1 else 0.0
            
            # Analyze trend
            trend = self._analyze_trend(values)
            
            # Detect anomalies
            anomalies = self._detect_anomalies(metrics, avg_value, std_dev)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                metric_name, component, values, trend, anomalies
            )
            
            analysis = PerformanceAnalysis(
                metric_name=metric_name,
                component=component,
                time_period=f"{hours}h",
                average=avg_value,
                min_value=min_value,
                max_value=max_value,
                median=median_value,
                std_deviation=std_dev,
                trend=trend,
                anomalies=anomalies,
                recommendations=recommendations
            )
            
            # Cache the analysis
            self.analysis_cache[cache_key] = (analysis, datetime.now())
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing performance: {str(e)}")
            raise
    
    def _analyze_trend(self, values: List[float]) -> str:
        """Analyze trend in metric values."""
        if len(values) < 10:
            return "insufficient_data"
        
        # Use linear regression to determine trend
        n = len(values)
        x = list(range(n))
        
        # Calculate slope
        x_mean = sum(x) / n
        y_mean = sum(values) / n
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return "stable"
        
        slope = numerator / denominator
        
        # Determine trend based on slope and significance
        slope_threshold = y_mean * 0.01  # 1% of mean as threshold
        
        if abs(slope) < slope_threshold:
            return "stable"
        elif slope > 0:
            return "increasing"
        else:
            return "decreasing"
    
    def _detect_anomalies(
        self,
        metrics: List[PerformanceMetric],
        mean_value: float,
        std_dev: float
    ) -> List[Dict[str, Any]]:
        """Detect anomalies in metric values."""
        if std_dev == 0:
            return []
        
        anomalies = []
        threshold = self.anomaly_threshold * std_dev
        
        for metric in metrics:
            deviation = abs(metric.value - mean_value)
            if deviation > threshold:
                anomalies.append({
                    "timestamp": metric.timestamp.isoformat(),
                    "value": metric.value,
                    "expected_range": [
                        mean_value - threshold,
                        mean_value + threshold
                    ],
                    "deviation": deviation,
                    "severity": "high" if deviation > 2 * threshold else "medium"
                })
        
        return anomalies
    
    def _generate_recommendations(
        self,
        metric_name: str,
        component: str,
        values: List[float],
        trend: str,
        anomalies: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate performance recommendations."""
        recommendations = []
        
        # Trend-based recommendations
        if trend == "increasing":
            if "cpu" in metric_name.lower() or "memory" in metric_name.lower():
                recommendations.append(f"Monitor {metric_name} closely - showing increasing trend")
                recommendations.append("Consider resource optimization or scaling")
            elif "response_time" in metric_name.lower():
                recommendations.append("Response times are increasing - investigate performance bottlenecks")
        
        elif trend == "decreasing":
            if "cpu" in metric_name.lower() or "memory" in metric_name.lower():
                recommendations.append(f"{metric_name} usage is decreasing - good performance trend")
            elif "throughput" in metric_name.lower():
                recommendations.append("Throughput is decreasing - investigate potential issues")
        
        # Anomaly-based recommendations
        high_severity_anomalies = [a for a in anomalies if a["severity"] == "high"]
        if high_severity_anomalies:
            recommendations.append(f"Detected {len(high_severity_anomalies)} high-severity anomalies")
            recommendations.append("Investigate system behavior during anomaly periods")
        
        # Component-specific recommendations
        if component == "database":
            if "response_time" in metric_name and max(values) > 1000:  # > 1 second
                recommendations.append("Database response times are high - consider query optimization")
            elif "connections" in metric_name and max(values) > 80:  # > 80% of typical limit
                recommendations.append("Database connection count is high - monitor for connection leaks")
        
        elif component == "api":
            if "response_time" in metric_name and max(values) > 500:  # > 500ms
                recommendations.append("API response times are high - optimize endpoint performance")
            elif "error_rate" in metric_name and max(values) > 5:  # > 5% error rate
                recommendations.append("API error rate is elevated - investigate error causes")
        
        elif component == "cache":
            if "hit_rate" in metric_name and min(values) < 80:  # < 80% hit rate
                recommendations.append("Cache hit rate is low - review caching strategy")
            elif "memory" in metric_name and max(values) > 80:  # > 80% memory usage
                recommendations.append("Cache memory usage is high - consider increasing cache size")
        
        # General recommendations
        if not recommendations:
            if len(anomalies) == 0 and trend == "stable":
                recommendations.append(f"{metric_name} performance is stable and healthy")
            else:
                recommendations.append(f"Continue monitoring {metric_name} for {component}")
        
        return recommendations
    
    async def get_component_performance_summary(
        self,
        component: str,
        hours: int = 24
    ) -> Dict[str, Any]:
        """Get comprehensive performance summary for a component."""
        try:
            # Get all metrics for this component
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT metric_name
                    FROM performance_metrics
                    WHERE component = ? AND timestamp > ?
                """, (component, cutoff_time.isoformat()))
                
                metric_names = [row[0] for row in cursor.fetchall()]
            
            # Analyze each metric
            analyses = {}
            for metric_name in metric_names:
                analysis = await self.analyze_performance(component, metric_name, hours)
                analyses[metric_name] = asdict(analysis)
            
            # Calculate overall component health score
            health_score = self._calculate_component_health_score(analyses)
            
            # Generate component-level recommendations
            component_recommendations = self._generate_component_recommendations(
                component, analyses, health_score
            )
            
            return {
                "component": component,
                "time_period": f"{hours}h",
                "health_score": health_score,
                "metrics_analyzed": len(metric_names),
                "metric_analyses": analyses,
                "recommendations": component_recommendations,
                "summary": {
                    "total_anomalies": sum(len(a["anomalies"]) for a in analyses.values()),
                    "metrics_with_issues": len([
                        a for a in analyses.values() 
                        if a["trend"] in ["increasing", "decreasing"] or a["anomalies"]
                    ]),
                    "stable_metrics": len([
                        a for a in analyses.values() 
                        if a["trend"] == "stable" and not a["anomalies"]
                    ])
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting component performance summary: {str(e)}")
            raise
    
    def _calculate_component_health_score(self, analyses: Dict[str, Dict]) -> float:
        """Calculate overall health score for a component (0-100)."""
        if not analyses:
            return 50.0  # Neutral score for no data
        
        scores = []
        
        for analysis in analyses.values():
            metric_score = 100.0
            
            # Penalize for anomalies
            anomaly_count = len(analysis["anomalies"])
            if anomaly_count > 0:
                metric_score -= min(anomaly_count * 10, 50)  # Max 50 point penalty
            
            # Penalize for concerning trends
            trend = analysis["trend"]
            if trend in ["increasing", "decreasing"]:
                # Determine if trend is concerning based on metric name
                metric_name = analysis["metric_name"].lower()
                if (trend == "increasing" and 
                    any(keyword in metric_name for keyword in ["cpu", "memory", "response_time", "error"])):
                    metric_score -= 20
                elif (trend == "decreasing" and 
                      any(keyword in metric_name for keyword in ["throughput", "hit_rate", "success"])):
                    metric_score -= 20
            
            # Bonus for stable performance
            if trend == "stable" and anomaly_count == 0:
                metric_score = min(metric_score + 10, 100)
            
            scores.append(max(metric_score, 0))
        
        return sum(scores) / len(scores) if scores else 50.0
    
    def _generate_component_recommendations(
        self,
        component: str,
        analyses: Dict[str, Dict],
        health_score: float
    ) -> List[str]:
        """Generate component-level recommendations."""
        recommendations = []
        
        # Health score based recommendations
        if health_score >= 90:
            recommendations.append(f"{component} is performing excellently")
        elif health_score >= 70:
            recommendations.append(f"{component} performance is good with minor areas for improvement")
        elif health_score >= 50:
            recommendations.append(f"{component} performance needs attention")
        else:
            recommendations.append(f"{component} performance requires immediate investigation")
        
        # Specific metric recommendations
        problematic_metrics = [
            name for name, analysis in analyses.items()
            if analysis["anomalies"] or analysis["trend"] in ["increasing", "decreasing"]
        ]
        
        if problematic_metrics:
            recommendations.append(
                f"Focus on these metrics: {', '.join(problematic_metrics[:3])}"
                + (f" and {len(problematic_metrics) - 3} others" if len(problematic_metrics) > 3 else "")
            )
        
        # Component-specific strategic recommendations
        if component == "database":
            if health_score < 70:
                recommendations.extend([
                    "Consider database query optimization",
                    "Review indexing strategy",
                    "Monitor connection pool usage"
                ])
        elif component == "api":
            if health_score < 70:
                recommendations.extend([
                    "Implement API response caching",
                    "Review endpoint performance",
                    "Consider load balancing"
                ])
        elif component == "cache":
            if health_score < 70:
                recommendations.extend([
                    "Optimize cache eviction policies",
                    "Review cache key strategies",
                    "Consider cache warming"
                ])
        
        return recommendations
    
    async def get_system_performance_overview(self, hours: int = 24) -> Dict[str, Any]:
        """Get system-wide performance overview."""
        try:
            # Get all components
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT component
                    FROM performance_metrics
                    WHERE timestamp > ?
                """, (cutoff_time.isoformat(),))
                
                components = [row[0] for row in cursor.fetchall()]
            
            # Get performance summary for each component
            component_summaries = {}
            total_health_score = 0
            
            for component in components:
                summary = await self.get_component_performance_summary(component, hours)
                component_summaries[component] = summary
                total_health_score += summary["health_score"]
            
            # Calculate system-wide metrics
            overall_health_score = total_health_score / len(components) if components else 0
            total_anomalies = sum(s["summary"]["total_anomalies"] for s in component_summaries.values())
            total_metrics = sum(s["metrics_analyzed"] for s in component_summaries.values())
            
            # Generate system-level recommendations
            system_recommendations = self._generate_system_recommendations(
                component_summaries, overall_health_score
            )
            
            return {
                "timestamp": datetime.now().isoformat(),
                "time_period": f"{hours}h",
                "overall_health_score": overall_health_score,
                "components_analyzed": len(components),
                "total_metrics": total_metrics,
                "total_anomalies": total_anomalies,
                "component_summaries": component_summaries,
                "system_recommendations": system_recommendations,
                "health_status": self._get_health_status(overall_health_score)
            }
            
        except Exception as e:
            logger.error(f"Error getting system performance overview: {str(e)}")
            raise
    
    def _generate_system_recommendations(
        self,
        component_summaries: Dict[str, Dict],
        overall_health_score: float
    ) -> List[str]:
        """Generate system-level recommendations."""
        recommendations = []
        
        # Overall system health
        if overall_health_score >= 90:
            recommendations.append("System performance is excellent across all components")
        elif overall_health_score >= 70:
            recommendations.append("System performance is good with some areas for optimization")
        elif overall_health_score >= 50:
            recommendations.append("System performance needs attention - multiple components showing issues")
        else:
            recommendations.append("System performance is critical - immediate action required")
        
        # Identify worst performing components
        worst_components = sorted(
            component_summaries.items(),
            key=lambda x: x[1]["health_score"]
        )[:3]
        
        if worst_components and worst_components[0][1]["health_score"] < 70:
            recommendations.append(
                f"Priority components for improvement: {', '.join([c[0] for c in worst_components])}"
            )
        
        # Resource scaling recommendations
        high_resource_usage = []
        for component, summary in component_summaries.items():
            for metric_name, analysis in summary["metric_analyses"].items():
                if ("cpu" in metric_name.lower() or "memory" in metric_name.lower()) and analysis["average"] > 80:
                    high_resource_usage.append(f"{component}:{metric_name}")
        
        if high_resource_usage:
            recommendations.append("Consider scaling resources for high-usage components")
        
        # Performance optimization recommendations
        slow_components = [
            component for component, summary in component_summaries.items()
            if any("response_time" in metric and analysis["average"] > 1000 
                   for metric, analysis in summary["metric_analyses"].items())
        ]
        
        if slow_components:
            recommendations.append(f"Optimize response times for: {', '.join(slow_components)}")
        
        return recommendations
    
    def _get_health_status(self, health_score: float) -> str:
        """Convert health score to status string."""
        if health_score >= 90:
            return "excellent"
        elif health_score >= 70:
            return "good"
        elif health_score >= 50:
            return "fair"
        else:
            return "poor"
    
    async def cleanup_old_metrics(self, days: int = None):
        """Clean up old performance metrics."""
        try:
            days = days or self.max_history_days
            cutoff_time = datetime.now() - timedelta(days=days)
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM performance_metrics
                    WHERE timestamp < ?
                """, (cutoff_time.isoformat(),))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"Cleaned up {deleted_count} old performance metrics")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Error cleaning up old metrics: {str(e)}")
            return 0
    
    async def export_performance_data(
        self,
        component: str = None,
        metric_name: str = None,
        hours: int = 24,
        format: str = "json"
    ) -> Dict[str, Any]:
        """Export performance data for analysis."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            query = """
                SELECT timestamp, metric_name, value, component, tags
                FROM performance_metrics
                WHERE timestamp > ?
            """
            params = [cutoff_time.isoformat()]
            
            if component:
                query += " AND component = ?"
                params.append(component)
            
            if metric_name:
                query += " AND metric_name = ?"
                params.append(metric_name)
            
            query += " ORDER BY timestamp ASC"
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                data = []
                for row in cursor.fetchall():
                    data.append({
                        "timestamp": row[0],
                        "metric_name": row[1],
                        "value": row[2],
                        "component": row[3],
                        "tags": json.loads(row[4]) if row[4] else {}
                    })
                
                return {
                    "export_timestamp": datetime.now().isoformat(),
                    "time_period": f"{hours}h",
                    "filters": {
                        "component": component,
                        "metric_name": metric_name
                    },
                    "data_points": len(data),
                    "data": data
                }
                
        except Exception as e:
            logger.error(f"Error exporting performance data: {str(e)}")
            raise

# Global performance analytics instance
performance_analytics = PerformanceAnalytics()

# Database initialization
async def init_performance_tables():
    """Initialize performance analytics database tables."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    component TEXT NOT NULL,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better query performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_performance_component_metric 
                ON performance_metrics(component, metric_name)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_performance_timestamp 
                ON performance_metrics(timestamp)
            """)
            
            conn.commit()
            logger.info("Performance analytics tables initialized")
            
    except Exception as e:
        logger.error(f"Error initializing performance tables: {str(e)}")
        raise