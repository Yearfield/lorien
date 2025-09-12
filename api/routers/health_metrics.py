"""
Health and metrics endpoints for observability.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import os

from ..core.metrics import get_metrics, get_health_status

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/metrics")
def get_health_metrics() -> Dict[str, Any]:
    """
    Get system health metrics.
    
    Returns metrics only when ANALYTICS_ENABLED=true.
    Returns 404 when analytics is disabled.
    """
    if not os.getenv("ANALYTICS_ENABLED", "false").lower() == "true":
        raise HTTPException(status_code=404, detail="Metrics not enabled")
    
    return get_metrics()

@router.get("/status")
def get_health_status_endpoint() -> Dict[str, Any]:
    """
    Get system health status.
    
    Returns health status based on current metrics and thresholds.
    """
    return get_health_status()

@router.get("/")
def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.
    
    Returns basic system information and status.
    """
    return {
        "status": "healthy",
        "service": "lorien-api",
        "version": "1.0.0",
        "analytics_enabled": os.getenv("ANALYTICS_ENABLED", "false").lower() == "true"
    }
