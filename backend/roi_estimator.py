# backend/roi_estimator.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional, Any
import logging
from datetime import datetime
from models import ROICalculationRequest, APIResponse
from database import log_execution
import json

logger = logging.getLogger(__name__)

router = APIRouter()

# ROI Configuration
ROI_CONFIG = {
    "cpm_ranges": {
        "gaming": (2.0, 4.0),
        "tech": (3.0, 6.0),
        "education": (4.0, 8.0),
        "entertainment": (2.0, 5.0),
        "business": (5.0, 10.0),
        "default": (3.0, 6.0)
    },
    "engagement_rates": {
        "high": 0.08,
        "medium": 0.05,
        "low": 0.02
    },
    "monetization_multipliers": {
        "ads_only": 1.0,
        "ads_affiliate": 1.5,
        "ads_affiliate_sponsors": 2.0,
        "full_monetization": 2.5
    }
}

def calculate_engagement_metrics(views: int, engagement_rate: float) -> Dict[str, int]:
    """
    Calculate engagement metrics based on views and engagement rate.
    
    Args:
        views (int): Number of views
        engagement_rate (float): Expected engagement rate
        
    Returns:
        Dict[str, int]: Calculated engagement metrics
    """
    return {
        "likes": int(views * engagement_rate),
        "comments": int(views * (engagement_rate * 0.1)),
        "shares": int(views * (engagement_rate * 0.05)),
        "subscribers": int(views * (engagement_rate * 0.02))
    }

def calculate_revenue(
    views: int,
    cpm: float,
    monetization_type: str = "ads_only"
) -> Dict[str, float]:
    """
    Calculate revenue based on views, CPM, and monetization type.
    
    Args:
        views (int): Number of views
        cpm (float): Cost per 1000 impressions
        monetization_type (str): Type of monetization
        
    Returns:
        Dict[str, float]: Revenue breakdown
    """
    # Get monetization multiplier
    multiplier = ROI_CONFIG["monetization_multipliers"].get(
        monetization_type,
        ROI_CONFIG["monetization_multipliers"]["ads_only"]
    )
    
    # Calculate base ad revenue
    ad_revenue = (views / 1000) * cpm
    
    # Calculate total revenue with multiplier
    total_revenue = ad_revenue * multiplier
    
    return {
        "ad_revenue": round(ad_revenue, 2),
        "total_revenue": round(total_revenue, 2),
        "revenue_per_view": round(total_revenue / views, 4) if views > 0 else 0
    }

def estimate_growth(
    views: int,
    engagement_rate: float,
    monetization_type: str = "ads_only"
) -> Dict[str, Any]:
    """
    Estimate channel growth metrics.
    
    Args:
        views (int): Number of views
        engagement_rate (float): Expected engagement rate
        monetization_type (str): Type of monetization
        
    Returns:
        Dict[str, Any]: Growth estimates
    """
    # Calculate engagement metrics
    engagement = calculate_engagement_metrics(views, engagement_rate)
    
    # Estimate subscriber growth
    subscriber_growth = engagement["subscribers"]
    
    # Estimate revenue growth
    revenue = calculate_revenue(views, ROI_CONFIG["cpm_ranges"]["default"][0], monetization_type)
    
    return {
        "subscriber_growth": subscriber_growth,
        "engagement_metrics": engagement,
        "revenue_estimates": revenue,
        "estimated_monthly_views": views * 1.2,  # Assuming 20% monthly growth
        "estimated_monthly_revenue": revenue["total_revenue"] * 1.2
    }

@router.post("/calculate", response_model=APIResponse)
async def calculate_roi(request: ROICalculationRequest):
    """
    Calculate ROI and engagement metrics.
    
    Args:
        request (ROICalculationRequest): ROI calculation parameters
        
    Returns:
        APIResponse: Calculation results
    """
    try:
        # Validate inputs
        if request.views < 0:
            raise HTTPException(
                status_code=400,
                detail="Views cannot be negative"
            )
        
        if not ROI_CONFIG["cpm_ranges"]["default"][0] <= request.cpm <= ROI_CONFIG["cpm_ranges"]["default"][1]:
            raise HTTPException(
                status_code=400,
                detail=f"CPM must be between {ROI_CONFIG['cpm_ranges']['default'][0]} and {ROI_CONFIG['cpm_ranges']['default'][1]}"
            )
        
        if not 0 <= request.engagement_rate <= 1:
            raise HTTPException(
                status_code=400,
                detail="Engagement rate must be between 0 and 1"
            )
        
        # Calculate metrics
        engagement = calculate_engagement_metrics(request.views, request.engagement_rate)
        revenue = calculate_revenue(request.views, request.cpm)
        growth = estimate_growth(request.views, request.engagement_rate)
        
        # Combine results
        result = {
            "views": request.views,
            "engagement": engagement,
            "revenue": revenue,
            "growth_estimates": growth,
            "calculated_at": datetime.utcnow().isoformat()
        }
        
        # Log the calculation
        log_execution(
            "roi_calculation",
            "success",
            {
                "views": request.views,
                "cpm": request.cpm,
                "engagement_rate": request.engagement_rate
            }
        )
        
        return APIResponse(
            status="success",
            data=result,
            message="ROI calculated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error calculating ROI: {str(e)}")
        log_execution("roi_calculation", "error", {"error": str(e)})
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating ROI: {str(e)}"
        )

@router.get("/cpm-ranges", response_model=APIResponse)
async def get_cpm_ranges():
    """Get CPM ranges for different categories."""
    try:
        return APIResponse(
            status="success",
            data={"cpm_ranges": ROI_CONFIG["cpm_ranges"]},
            message="CPM ranges retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error retrieving CPM ranges: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving CPM ranges: {str(e)}"
        )

@router.get("/monetization-types", response_model=APIResponse)
async def get_monetization_types():
    """Get available monetization types and their multipliers."""
    try:
        return APIResponse(
            status="success",
            data={"monetization_types": ROI_CONFIG["monetization_multipliers"]},
            message="Monetization types retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error retrieving monetization types: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving monetization types: {str(e)}"
        )