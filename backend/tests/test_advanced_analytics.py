import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
from datetime import datetime, timedelta

from main import app
from ai_modules.advanced_analytics_utils import (
    normalize_video_data,
    calculate_video_performance_score,
    calculate_competitive_metrics
)

client = TestClient(app)

# Sample test data
SAMPLE_VIDEO_DATA = [
    {
        "title": "Test Video 1",
        "views": 10000,
        "likes": 500,
        "comments": 50,
        "shares": 25,
        "duration": 600,
        "published_at": "2024-01-01T00:00:00Z",
        "category": "tech",
        "ad_revenue": 100,
        "sponsorship_revenue": 200,
        "affiliate_revenue": 50
    },
    {
        "title": "Test Video 2",
        "views": 15000,
        "likes": 750,
        "comments": 75,
        "shares": 40,
        "duration": 480,
        "published_at": "2024-01-15T00:00:00Z",
        "category": "tech",
        "ad_revenue": 150,
        "sponsorship_revenue": 300,
        "affiliate_revenue": 75
    }
]

SAMPLE_CHANNEL_DATA = {
    "channel_id": "test_channel",
    "videos": SAMPLE_VIDEO_DATA,
    "subscriber_count": 50000,
    "total_views": 25000
}

class TestAdvancedAnalyticsUtils:
    """Test utility functions for advanced analytics."""
    
    def test_normalize_video_data(self):
        """Test video data normalization."""
        normalized = normalize_video_data(SAMPLE_VIDEO_DATA)
        assert len(normalized) == 2
        assert all('engagement_score' in video for video in normalized)
        assert all('performance_score' in video for video in normalized)
        assert all('revenue_total' in video for video in normalized)
        
        # Check calculated fields
        first_video = normalized[0]
        expected_engagement = (500 + 50 + 25) / 10000
        assert abs(first_video['engagement_score'] - expected_engagement) < 0.001
        assert first_video['revenue_total'] == 350  # 100 + 200 + 50
    
    def test_calculate_video_performance_score(self):
        """Test performance score calculation."""
        video_data = SAMPLE_VIDEO_DATA[0].copy()
        video_data['engagement_score'] = 0.0575  # Pre-calculated
        
        score = calculate_video_performance_score(video_data)
        
        assert isinstance(score, float)
        assert 0 <= score <= 100
        assert score > 0  # Should have some positive score
    
    def test_calculate_competitive_metrics(self):
        """Test competitive metrics calculation."""
        industry_benchmarks = {
            "avg_views": 75000,
            "avg_engagement": 0.045,
            "avg_retention": 0.65,
            "revenue_per_video": 750
        }
        
        metrics = calculate_competitive_metrics(SAMPLE_CHANNEL_DATA, industry_benchmarks)
        
        assert 'performance_vs_industry' in metrics
        assert 'strengths' in metrics
        assert 'improvement_areas' in metrics
        assert 'competitive_score' in metrics
        
        # Check that competitive score is calculated
        assert isinstance(metrics['competitive_score'], (int, float))
        assert 0 <= metrics['competitive_score'] <= 100

class TestAdvancedAnalyticsEndpoints:
    """Test advanced analytics API endpoints."""
    
    def test_advanced_analytics_comprehensive(self):
        """Test comprehensive analytics endpoint."""
        request_data = {
            "channel_data": SAMPLE_CHANNEL_DATA,
            "analysis_type": "comprehensive",
            "time_period": 90
        }
        
        with patch('ai_modules.advanced_analytics_utils.calculate_comprehensive_analysis') as mock_analysis:
            mock_analysis.return_value = {
                "total_views": 25000,
                "avg_engagement": 0.055,
                "total_revenue": 875,
                "performance_score": 78.5
            }
            
            response = client.post("/api/analytics/advanced", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "total_views" in data["data"]
            assert "performance_score" in data["data"]
    
    def test_advanced_analytics_predictive(self):
        """Test predictive analytics endpoint."""
        request_data = {
            "channel_data": SAMPLE_CHANNEL_DATA,
            "analysis_type": "predictive",
            "time_period": 90
        }
        
        with patch('ai_modules.advanced_analytics_utils.generate_predictive_analysis') as mock_analysis:
            mock_analysis.return_value = {
                "growth_forecast": [
                    {"period": "Month 1", "predicted_views": 30000},
                    {"period": "Month 2", "predicted_views": 35000}
                ],
                "trend_analysis": [
                    {"metric": "views", "direction": "up", "change": 15.5, "confidence": 85}
                ]
            }
            
            response = client.post("/api/analytics/advanced", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "growth_forecast" in data["data"]
            assert "trend_analysis" in data["data"]
    
    def test_performance_insights(self):
        """Test performance insights endpoint."""
        request_data = {
            "channel_data": SAMPLE_CHANNEL_DATA
        }
        
        with patch('ai_modules.advanced_analytics_utils.generate_performance_insights') as mock_insights:
            mock_insights.return_value = {
                "score_breakdown": [
                    {"category": "Content Quality", "score": 85},
                    {"category": "Engagement", "score": 72}
                ],
                "top_content": [
                    {"title": "Test Video 2", "performance_score": 88.5}
                ]
            }
            
            response = client.post("/api/analytics/performance-insights", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "score_breakdown" in data["data"]
            assert "top_content" in data["data"]
    
    def test_growth_forecast(self):
        """Test growth forecast endpoint."""
        request_data = {
            "channel_data": SAMPLE_CHANNEL_DATA,
            "forecast_period": 30
        }
        
        with patch('ai_modules.advanced_analytics_utils.calculate_growth_forecast') as mock_forecast:
            mock_forecast.return_value = {
                "forecast_data": [
                    {"date": "2024-02-01", "predicted_views": 28000, "confidence": 0.85},
                    {"date": "2024-02-15", "predicted_views": 32000, "confidence": 0.80}
                ],
                "growth_rate": 0.125,
                "confidence_interval": {"lower": 0.10, "upper": 0.15}
            }
            
            response = client.post("/api/analytics/growth-forecast", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "forecast_data" in data["data"]
            assert "growth_rate" in data["data"]
    
    def test_revenue_analysis(self):
        """Test revenue analysis endpoint."""
        request_data = {
            "videos": SAMPLE_VIDEO_DATA
        }
        
        with patch('ai_modules.advanced_analytics_utils.analyze_revenue_streams') as mock_analysis:
            mock_analysis.return_value = {
                "revenue_breakdown": [
                    {"name": "Ad Revenue", "value": 250},
                    {"name": "Sponsorships", "value": 500},
                    {"name": "Affiliates", "value": 125}
                ],
                "rpm_analysis": [
                    {"category": "tech", "rpm": 3.5}
                ],
                "optimization_insights": [
                    {"category": "Sponsorships", "insight": "Increase sponsor integration"}
                ]
            }
            
            response = client.post("/api/analytics/revenue-analysis", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "revenue_breakdown" in data["data"]
            assert "rpm_analysis" in data["data"]
    
    def test_optimization_suggestions(self):
        """Test optimization suggestions endpoint."""
        request_data = {
            "channel_data": SAMPLE_CHANNEL_DATA
        }
        
        with patch('ai_modules.advanced_analytics_utils.generate_optimization_suggestions') as mock_suggestions:
            mock_suggestions.return_value = {
                "content_recommendations": [
                    {
                        "category": "Title Optimization",
                        "recommendation": "Use more engaging titles",
                        "impact_score": 8,
                        "steps": ["Research trending keywords", "A/B test titles"]
                    }
                ],
                "posting_optimization": {
                    "best_day": {"day": "Tuesday", "performance": 1.25},
                    "best_time": {"time": "14:00", "performance": 1.15},
                    "frequency": "3 times per week"
                },
                "seo_optimization": {
                    "title": {"optimal_length": 60, "keywords": ["tech", "tutorial"]},
                    "tags": {"recommended_count": 10, "high_impact": ["technology", "howto"]}
                }
            }
            
            response = client.post("/api/analytics/optimization-suggestions", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "content_recommendations" in data["data"]
            assert "posting_optimization" in data["data"]
    
    def test_audience_insights(self):
        """Test audience insights endpoint."""
        request_data = {
            "channel_data": SAMPLE_CHANNEL_DATA
        }
        
        with patch('ai_modules.advanced_analytics_utils.analyze_audience_insights') as mock_insights:
            mock_insights.return_value = {
                "demographics": [
                    {"age_group": "18-24", "percentage": 35},
                    {"age_group": "25-34", "percentage": 45}
                ],
                "engagement_patterns": [
                    {"hour": 14, "engagement_rate": 0.065},
                    {"hour": 20, "engagement_rate": 0.058}
                ],
                "avg_retention_rate": 0.68,
                "avg_watch_time": 420,
                "subscriber_conversion_rate": 0.025
            }
            
            response = client.post("/api/analytics/audience-insights", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "demographics" in data["data"]
            assert "engagement_patterns" in data["data"]
    
    def test_industry_benchmarks(self):
        """Test industry benchmarks endpoint."""
        response = client.get("/api/analytics/benchmarks/tech")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "avg_views" in data["data"]
        assert "avg_engagement" in data["data"]
        assert "revenue_per_video" in data["data"]
    
    def test_competitive_analysis(self):
        """Test competitive analysis endpoint."""
        request_data = {
            "channel_data": SAMPLE_CHANNEL_DATA
        }
        
        response = client.post("/api/analytics/competitive-analysis", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "primary_category" in data["data"]
        assert "industry_benchmarks" in data["data"]
    
    def test_content_lifecycle(self):
        """Test content lifecycle analysis endpoint."""
        request_data = {
            "videos": SAMPLE_VIDEO_DATA
        }
        
        with patch('ai_modules.advanced_analytics_utils.analyze_content_lifecycle') as mock_analysis:
            mock_analysis.return_value = {
                "lifecycle_stages": [
                    {"stage": "Launch", "duration_days": 7, "view_percentage": 0.6},
                    {"stage": "Growth", "duration_days": 30, "view_percentage": 0.3},
                    {"stage": "Mature", "duration_days": 90, "view_percentage": 0.1}
                ],
                "peak_performance_day": 3,
                "longevity_score": 75
            }
            
            response = client.post("/api/analytics/content-lifecycle", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "lifecycle_stages" in data["data"]
            assert "longevity_score" in data["data"]
    
    def test_retention_analysis(self):
        """Test audience retention analysis endpoint."""
        request_data = {
            "videos": SAMPLE_VIDEO_DATA
        }
        
        with patch('ai_modules.advanced_analytics_utils.calculate_audience_retention_metrics') as mock_analysis:
            mock_analysis.return_value = {
                "avg_retention_rate": 0.68,
                "retention_curve": [
                    {"timestamp": 0, "retention_percentage": 100},
                    {"timestamp": 30, "retention_percentage": 85},
                    {"timestamp": 60, "retention_percentage": 70}
                ],
                "drop_off_points": [
                    {"timestamp": 45, "drop_percentage": 15, "reason": "Introduction too long"}
                ],
                "engagement_hotspots": [
                    {"timestamp": 120, "engagement_spike": 1.25}
                ]
            }
            
            response = client.post("/api/analytics/retention-analysis", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "retention_curve" in data["data"]
            assert "drop_off_points" in data["data"]
    
    def test_export_analytics_json(self):
        """Test analytics data export in JSON format."""
        response = client.get("/api/analytics/export/json?channel_id=test_channel")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        assert "attachment" in response.headers.get("content-disposition", "")
    
    def test_export_analytics_csv(self):
        """Test analytics data export in CSV format."""
        response = client.get("/api/analytics/export/csv")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment" in response.headers.get("content-disposition", "")
    
    def test_invalid_analysis_type(self):
        """Test handling of invalid analysis type."""
        request_data = {
            "channel_data": SAMPLE_CHANNEL_DATA,
            "analysis_type": "invalid_type"
        }
        
        with patch('ai_modules.advanced_analytics_utils.calculate_comprehensive_analysis') as mock_analysis:
            mock_analysis.return_value = {"fallback": "data"}
            
            response = client.post("/api/analytics/advanced", json=request_data)
            
            # Should fallback to comprehensive analysis
            assert response.status_code == 200
            mock_analysis.assert_called_once()
    
    def test_empty_video_data_error(self):
        """Test error handling for empty video data."""
        request_data = {
            "channel_data": {"videos": []},
            "analysis_type": "comprehensive"
        }
        
        response = client.post("/api/analytics/advanced", json=request_data)
        
        assert response.status_code == 400
        assert "No video data provided" in response.json()["detail"]
    
    def test_malformed_request_error(self):
        """Test error handling for malformed requests."""
        request_data = {
            "invalid_field": "invalid_data"
        }
        
        response = client.post("/api/analytics/advanced", json=request_data)
        
        assert response.status_code == 422  # Validation error

class TestAnalyticsIntegration:
    """Integration tests for analytics functionality."""
    
    @pytest.mark.asyncio
    async def test_full_analytics_pipeline(self):
        """Test complete analytics pipeline from data input to insights."""
        # This would test the full flow in a real environment
        # For now, we'll test the key components work together
        
        from ai_modules.advanced_analytics_utils import (
            normalize_video_data,
            calculate_comprehensive_analysis
        )
        
        # Normalize data
        normalized_videos = normalize_video_data(SAMPLE_VIDEO_DATA)
        
        # Run comprehensive analysis
        analysis_result = await calculate_comprehensive_analysis(normalized_videos, SAMPLE_CHANNEL_DATA)
        
        # Verify the pipeline produces expected results
        assert isinstance(analysis_result, dict)
        assert len(analysis_result) > 0
        
        # Check that all major analysis components are present
        expected_keys = [
            'overview_metrics',
            'performance_insights',
            'trend_analysis',
            'recommendations'
        ]
        
        # At least some of these should be present
        assert any(key in analysis_result for key in expected_keys)
    
    def test_analytics_data_consistency(self):
        """Test that analytics calculations are consistent across different calls."""
        normalized_videos = normalize_video_data(SAMPLE_VIDEO_DATA)
        
        # Calculate performance scores multiple times
        scores = []
        for _ in range(5):
            score = calculate_video_performance_score(normalized_videos[0])
            scores.append(score)
        
        # All scores should be identical (deterministic calculation)
        assert all(abs(score - scores[0]) < 0.001 for score in scores)
    
    def test_analytics_edge_cases(self):
        """Test analytics with edge case data."""
        edge_case_data = [
            {
                "title": "Edge Case Video",
                "views": 0,
                "likes": 0,
                "comments": 0,
                "shares": 0,
                "duration": 1,
                "published_at": "2024-01-01T00:00:00Z",
                "category": "unknown",
                "ad_revenue": 0,
                "sponsorship_revenue": 0,
                "affiliate_revenue": 0
            }
        ]
        
        # Should not crash with zero values
        normalized = normalize_video_data(edge_case_data)
        assert len(normalized) == 1
        assert normalized[0]['engagement_score'] == 0
        assert normalized[0]['revenue_total'] == 0
        
        # Performance score should handle zero values gracefully
        score = calculate_video_performance_score(normalized[0])
        assert isinstance(score, (int, float))
        assert score >= 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])