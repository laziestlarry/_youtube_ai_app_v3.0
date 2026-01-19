from __future__ import annotations

import csv
import io
import inspect
import json
import math
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except Exception:
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def _clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))


def normalize_video_data(videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalize video dicts and add derived metrics used throughout analytics.

    Adds:
      - engagement_score: (likes + comments + shares) / views
      - revenue_total: ad_revenue + sponsorship_revenue + affiliate_revenue
      - performance_score: 0..100 deterministic score
    """
    normalized: List[Dict[str, Any]] = []
    for video in videos or []:
        record = dict(video or {})

        views = _safe_int(record.get("views"))
        likes = _safe_int(record.get("likes"))
        comments = _safe_int(record.get("comments"))
        shares = _safe_int(record.get("shares"))

        if views > 0:
            engagement_score = (likes + comments + shares) / float(views)
        else:
            engagement_score = 0.0

        record["engagement_score"] = float(engagement_score)

        revenue_total = (
            _safe_float(record.get("ad_revenue"))
            + _safe_float(record.get("sponsorship_revenue"))
            + _safe_float(record.get("affiliate_revenue"))
        )
        record["revenue_total"] = revenue_total if revenue_total.is_integer() is False else int(revenue_total)

        record["performance_score"] = calculate_video_performance_score(record)
        normalized.append(record)

    return normalized


def calculate_video_performance_score(video: Dict[str, Any]) -> float:
    """
    Deterministic 0..100 score combining reach, engagement and revenue.
    """
    views = _safe_int(video.get("views"))
    engagement = _safe_float(video.get("engagement_score"))
    revenue_total = _safe_float(video.get("revenue_total"))

    views_component = 0.0
    if views > 0:
        views_component = (math.log1p(views) / math.log1p(100_000)) * 50.0

    engagement_component = (engagement / 0.10) * 35.0
    revenue_component = (revenue_total / 1_000.0) * 15.0

    score = _clamp(views_component, 0.0, 50.0) + _clamp(engagement_component, 0.0, 35.0) + _clamp(
        revenue_component, 0.0, 15.0
    )
    return float(round(_clamp(score, 0.0, 100.0), 4))


def calculate_competitive_metrics(channel_data: Dict[str, Any], industry_benchmarks: Dict[str, Any]) -> Dict[str, Any]:
    videos = normalize_video_data(list((channel_data or {}).get("videos") or []))
    if not videos:
        avg_views = 0.0
        avg_engagement = 0.0
        avg_revenue = 0.0
    else:
        avg_views = sum(_safe_int(v.get("views")) for v in videos) / float(len(videos))
        avg_engagement = sum(_safe_float(v.get("engagement_score")) for v in videos) / float(len(videos))
        avg_revenue = sum(_safe_float(v.get("revenue_total")) for v in videos) / float(len(videos))

    views_b = max(_safe_float(industry_benchmarks.get("avg_views"), 1.0), 1.0)
    engagement_b = max(_safe_float(industry_benchmarks.get("avg_engagement"), 0.01), 0.0001)
    revenue_b = max(_safe_float(industry_benchmarks.get("revenue_per_video"), 1.0), 1.0)

    views_vs = (avg_views / views_b) * 100.0
    engagement_vs = (avg_engagement / engagement_b) * 100.0
    revenue_vs = (avg_revenue / revenue_b) * 100.0

    strengths: List[str] = []
    improvement_areas: List[str] = []
    for name, value in (("views", views_vs), ("engagement", engagement_vs), ("revenue", revenue_vs)):
        if value >= 100.0:
            strengths.append(name)
        else:
            improvement_areas.append(name)

    competitive_score = _clamp((views_vs + engagement_vs + revenue_vs) / 3.0, 0.0, 100.0)

    return {
        "performance_vs_industry": {
            "views_vs_benchmark": round(views_vs, 2),
            "engagement_vs_benchmark": round(engagement_vs, 2),
            "revenue_vs_benchmark": round(revenue_vs, 2),
        },
        "strengths": strengths,
        "improvement_areas": improvement_areas,
        "competitive_score": round(competitive_score, 2),
    }


def get_industry_benchmarks(niche: str) -> Dict[str, Any]:
    niche_key = (niche or "general").strip().lower()
    presets = {
        "tech": {"avg_views": 75_000, "avg_engagement": 0.045, "avg_retention": 0.65, "revenue_per_video": 750},
        "general": {"avg_views": 50_000, "avg_engagement": 0.035, "avg_retention": 0.60, "revenue_per_video": 500},
    }
    return dict(presets.get(niche_key, presets["general"]))


async def calculate_comprehensive_analysis(videos: List[Dict[str, Any]], channel_data: Dict[str, Any]) -> Dict[str, Any]:
    normalized = normalize_video_data(videos or list((channel_data or {}).get("videos") or []))
    total_views = sum(_safe_int(v.get("views")) for v in normalized)
    total_revenue = sum(_safe_float(v.get("revenue_total")) for v in normalized)
    avg_engagement = (sum(_safe_float(v.get("engagement_score")) for v in normalized) / len(normalized)) if normalized else 0.0
    avg_performance = (
        sum(_safe_float(v.get("performance_score")) for v in normalized) / len(normalized) if normalized else 0.0
    )

    return {
        "overview_metrics": {
            "total_videos": len(normalized),
            "total_views": total_views,
            "total_revenue": round(total_revenue, 2),
            "avg_engagement": round(avg_engagement, 4),
            "avg_performance": round(avg_performance, 2),
        },
        "performance_insights": {"top_videos": sorted(normalized, key=lambda v: _safe_float(v.get("performance_score")), reverse=True)[:5]},
        "trend_analysis": {"direction": "up" if total_views > 0 else "flat"},
        "recommendations": ["Increase posting consistency", "A/B test titles", "Double down on best categories"],
    }


def generate_predictive_analysis(channel_data: Dict[str, Any], time_period: int = 90) -> Dict[str, Any]:
    videos = normalize_video_data(list((channel_data or {}).get("videos") or []))
    total_views = sum(_safe_int(v.get("views")) for v in videos)
    baseline = total_views / max(len(videos), 1)
    return {
        "growth_forecast": [{"period": "Next Period", "predicted_views": int(baseline * 1.15)}],
        "trend_analysis": [{"metric": "views", "direction": "up" if baseline > 0 else "flat", "change": 15.0, "confidence": 75}],
    }


def generate_performance_insights(channel_data: Dict[str, Any]) -> Dict[str, Any]:
    videos = normalize_video_data(list((channel_data or {}).get("videos") or []))
    top = sorted(videos, key=lambda v: _safe_float(v.get("performance_score")), reverse=True)[:3]
    return {
        "score_breakdown": [
            {"category": "Reach", "score": round(sum(_safe_float(v.get("performance_score")) for v in videos) / max(len(videos), 1), 2)},
            {"category": "Engagement", "score": round(100 * (sum(_safe_float(v.get("engagement_score")) for v in videos) / max(len(videos), 1)), 2)},
        ],
        "top_content": [{"title": v.get("title", ""), "performance_score": v.get("performance_score", 0)} for v in top],
    }


def calculate_growth_forecast(channel_data: Dict[str, Any], forecast_period: int = 30) -> Dict[str, Any]:
    forecast_period = int(forecast_period or 30)
    return {
        "forecast_data": [
            {"date": datetime.now(timezone.utc).date().isoformat(), "predicted_views": 0, "confidence": 0.8}
        ],
        "growth_rate": 0.0,
        "confidence_interval": {"lower": 0.0, "upper": 0.0},
    }


def analyze_revenue_streams(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    normalized = normalize_video_data(videos or [])
    total_ad = sum(_safe_float(v.get("ad_revenue")) for v in normalized)
    total_spon = sum(_safe_float(v.get("sponsorship_revenue")) for v in normalized)
    total_aff = sum(_safe_float(v.get("affiliate_revenue")) for v in normalized)
    return {
        "revenue_breakdown": [
            {"name": "Ad Revenue", "value": round(total_ad, 2)},
            {"name": "Sponsorships", "value": round(total_spon, 2)},
            {"name": "Affiliates", "value": round(total_aff, 2)},
        ],
        "rpm_analysis": [],
        "optimization_insights": [],
    }


def generate_optimization_suggestions(channel_data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "content_recommendations": [],
        "posting_optimization": {},
        "seo_optimization": {},
    }


def analyze_audience_insights(channel_data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "demographics": [],
        "engagement_patterns": [],
        "avg_retention_rate": 0.0,
        "avg_watch_time": 0,
        "subscriber_conversion_rate": 0.0,
    }


def analyze_content_lifecycle(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "lifecycle_stages": [],
        "peak_performance_day": 0,
        "longevity_score": 0,
    }


def calculate_audience_retention_metrics(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "avg_retention_rate": 0.0,
        "retention_curve": [],
        "drop_off_points": [],
        "engagement_hotspots": [],
    }


def export_analytics_json(channel_id: str, payload: Dict[str, Any]) -> bytes:
    data = {"channel_id": channel_id, "exported_at": datetime.now(timezone.utc).isoformat(), "data": payload}
    return json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")


def export_analytics_csv(rows: Iterable[Dict[str, Any]]) -> bytes:
    output = io.StringIO()
    row_list = list(rows)
    fieldnames: List[str] = sorted({key for row in row_list for key in (row or {}).keys()})
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in row_list:
        writer.writerow(row or {})
    return output.getvalue().encode("utf-8")


async def maybe_await(value: Any) -> Any:
    if inspect.isawaitable(value):
        return await value
    return value

