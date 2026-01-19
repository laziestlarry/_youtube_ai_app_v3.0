from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field

import ai_modules.advanced_analytics_utils as analytics_utils


router = APIRouter()


class ChannelData(BaseModel):
    channel_id: Optional[str] = None
    videos: List[Dict[str, Any]] = Field(default_factory=list)
    subscriber_count: Optional[int] = None
    total_views: Optional[int] = None


class AdvancedAnalyticsRequest(BaseModel):
    channel_data: ChannelData
    analysis_type: str = "comprehensive"
    time_period: int = 90


class ChannelOnlyRequest(BaseModel):
    channel_data: ChannelData


class GrowthForecastRequest(BaseModel):
    channel_data: ChannelData
    forecast_period: int = 30


class VideosRequest(BaseModel):
    videos: List[Dict[str, Any]] = Field(default_factory=list)


@router.post("/advanced")
async def advanced_analytics(request: AdvancedAnalyticsRequest):
    videos = request.channel_data.videos
    if not videos:
        raise HTTPException(status_code=400, detail="No video data provided")

    analysis_type = (request.analysis_type or "comprehensive").strip().lower()
    if analysis_type == "predictive":
        result = analytics_utils.generate_predictive_analysis(request.channel_data.model_dump(), request.time_period)
    else:
        # Fallback to comprehensive for unknown types (test expects this behavior).
        result = analytics_utils.calculate_comprehensive_analysis(videos, request.channel_data.model_dump())
        result = await analytics_utils.maybe_await(result)

    return {"status": "success", "data": result, "analysis_type": analysis_type}


@router.post("/performance-insights")
async def performance_insights(request: ChannelOnlyRequest):
    result = analytics_utils.generate_performance_insights(request.channel_data.model_dump())
    result = await analytics_utils.maybe_await(result)
    return {"status": "success", "data": result}


@router.post("/growth-forecast")
async def growth_forecast(request: GrowthForecastRequest):
    result = analytics_utils.calculate_growth_forecast(request.channel_data.model_dump(), request.forecast_period)
    result = await analytics_utils.maybe_await(result)
    return {"status": "success", "data": result}


@router.post("/revenue-analysis")
async def revenue_analysis(request: VideosRequest):
    result = analytics_utils.analyze_revenue_streams(request.videos)
    result = await analytics_utils.maybe_await(result)
    return {"status": "success", "data": result}


@router.post("/optimization-suggestions")
async def optimization_suggestions(request: ChannelOnlyRequest):
    result = analytics_utils.generate_optimization_suggestions(request.channel_data.model_dump())
    result = await analytics_utils.maybe_await(result)
    return {"status": "success", "data": result}


@router.post("/audience-insights")
async def audience_insights(request: ChannelOnlyRequest):
    result = analytics_utils.analyze_audience_insights(request.channel_data.model_dump())
    result = await analytics_utils.maybe_await(result)
    return {"status": "success", "data": result}


@router.get("/benchmarks/{niche}")
async def industry_benchmarks(niche: str):
    data = analytics_utils.get_industry_benchmarks(niche)
    return {"status": "success", "data": data}


@router.post("/competitive-analysis")
async def competitive_analysis(request: ChannelOnlyRequest):
    videos = request.channel_data.videos
    primary_category = "general"
    if videos and isinstance(videos[0], dict) and videos[0].get("category"):
        primary_category = str(videos[0].get("category"))

    industry = analytics_utils.get_industry_benchmarks(primary_category)
    metrics = analytics_utils.calculate_competitive_metrics(request.channel_data.model_dump(), industry)
    return {"status": "success", "data": {"primary_category": primary_category, "industry_benchmarks": industry, **metrics}}


@router.post("/content-lifecycle")
async def content_lifecycle(request: VideosRequest):
    result = analytics_utils.analyze_content_lifecycle(request.videos)
    result = await analytics_utils.maybe_await(result)
    return {"status": "success", "data": result}


@router.post("/retention-analysis")
async def retention_analysis(request: VideosRequest):
    result = analytics_utils.calculate_audience_retention_metrics(request.videos)
    result = await analytics_utils.maybe_await(result)
    return {"status": "success", "data": result}


@router.get("/export/json")
async def export_json(channel_id: str = "unknown"):
    payload = {"note": "export placeholder", "channel_id": channel_id}
    body = analytics_utils.export_analytics_json(channel_id, payload)
    headers = {"Content-Disposition": 'attachment; filename="analytics_export.json"'}
    return Response(content=body, media_type="application/json", headers=headers)


@router.get("/export/csv")
async def export_csv():
    body = analytics_utils.export_analytics_csv([{"example": "row"}])
    headers = {"Content-Disposition": 'attachment; filename="analytics_export.csv"'}
    return Response(content=body, media_type="text/csv", headers=headers)
