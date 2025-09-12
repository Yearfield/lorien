"""
Performance monitoring and optimization endpoints.

Provides endpoints for monitoring database performance, managing indexes,
and streaming large exports.
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from typing import Dict, Any, Optional, List
import logging
import io
import csv

from ..dependencies import get_repository
from storage.sqlite import SQLiteRepository
from ..repositories.performance import PerformanceOptimizer, StreamingCSVExporter, get_cache_stats, clear_navigation_cache

router = APIRouter(tags=["performance"])

@router.get("/admin/performance/database-stats")
async def get_database_stats(repo: SQLiteRepository = Depends(get_repository)):
    """
    Get comprehensive database performance statistics.
    
    Returns:
        200 with database statistics including:
        - Node counts by type and depth
        - Index information
        - Database size
        - Performance metrics
    """
    try:
        with repo._get_connection() as conn:
            optimizer = PerformanceOptimizer(conn)
            stats = optimizer.get_database_stats()
            
            return {
                "database_stats": stats,
                "cache_stats": get_cache_stats(),
                "status": "healthy"
            }
    
    except Exception as e:
        logging.error(f"Error getting database stats: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get database statistics",
                "message": str(e)
            }
        )

@router.post("/admin/performance/create-indexes")
async def create_performance_indexes(repo: SQLiteRepository = Depends(get_repository)):
    """
    Create performance-optimized database indexes.
    
    This operation is safe to run multiple times and will only create
    indexes that don't already exist.
    
    Returns:
        200 with created indexes information
    """
    try:
        with repo._get_connection() as conn:
            optimizer = PerformanceOptimizer(conn)
            created_indexes = optimizer.create_performance_indexes()
            
            return {
                "created_indexes": created_indexes,
                "index_count": len(created_indexes),
                "status": "completed",
                "message": f"Successfully created {len(created_indexes)} performance indexes"
            }
    
    except Exception as e:
        logging.error(f"Error creating performance indexes: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to create performance indexes",
                "message": str(e)
            }
        )

@router.get("/admin/performance/analyze-query")
async def analyze_query_performance(
    query: str,
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Analyze the performance of a specific SQL query.
    
    Args:
        query: SQL query to analyze
        
    Returns:
        200 with query performance analysis
    """
    try:
        with repo._get_connection() as conn:
            optimizer = PerformanceOptimizer(conn)
            analysis = optimizer.analyze_query_performance(query)
            
            return {
                "query_analysis": analysis,
                "status": "completed"
            }
    
    except Exception as e:
        logging.error(f"Error analyzing query performance: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to analyze query performance",
                "message": str(e)
            }
        )

@router.get("/admin/performance/export/tree-streaming")
async def export_tree_streaming(
    batch_size: int = 1000,
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Stream the entire tree as CSV for large datasets.
    
    Args:
        batch_size: Number of rows to process per batch (default: 1000)
        
    Returns:
        Streaming CSV response
    """
    try:
        def generate_csv():
            with repo._get_connection() as conn:
                exporter = StreamingCSVExporter(conn)
                for chunk in exporter.export_tree_streaming(batch_size):
                    yield chunk
        
        return StreamingResponse(
            generate_csv(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=tree_export.csv"}
        )
    
    except Exception as e:
        logging.error(f"Error streaming tree export: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to stream tree export",
                "message": str(e)
            }
        )

@router.get("/admin/performance/export/children-streaming/{parent_id}")
async def export_children_streaming(
    parent_id: int,
    batch_size: int = 100,
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Stream children data for a specific parent as CSV.
    
    Args:
        parent_id: Parent node ID
        batch_size: Number of rows to process per batch (default: 100)
        
    Returns:
        Streaming CSV response
    """
    try:
        def generate_csv():
            with repo._get_connection() as conn:
                exporter = StreamingCSVExporter(conn)
                for chunk in exporter.export_children_streaming(parent_id, batch_size):
                    yield chunk
        
        return StreamingResponse(
            generate_csv(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=children_{parent_id}_export.csv"}
        )
    
    except Exception as e:
        logging.error(f"Error streaming children export: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to stream children export",
                "message": str(e)
            }
        )

@router.get("/admin/performance/cache-stats")
async def get_cache_statistics():
    """
    Get navigation cache statistics.
    
    Returns:
        200 with cache performance metrics
    """
    try:
        stats = get_cache_stats()
        return {
            "cache_stats": stats,
            "status": "healthy"
        }
    
    except Exception as e:
        logging.error(f"Error getting cache stats: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get cache statistics",
                "message": str(e)
            }
        )

@router.post("/admin/performance/clear-cache")
async def clear_cache():
    """
    Clear the navigation cache.
    
    Returns:
        200 with confirmation
    """
    try:
        clear_navigation_cache()
        return {
            "status": "completed",
            "message": "Navigation cache cleared successfully"
        }
    
    except Exception as e:
        logging.error(f"Error clearing cache: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to clear cache",
                "message": str(e)
            }
        )

@router.get("/admin/performance/health")
async def get_performance_health(repo: SQLiteRepository = Depends(get_repository)):
    """
    Get overall performance health status.
    
    Returns:
        200 with performance health metrics
    """
    try:
        with repo._get_connection() as conn:
            optimizer = PerformanceOptimizer(conn)
            db_stats = optimizer.get_database_stats()
            cache_stats = get_cache_stats()
            
            # Determine health status based on metrics
            total_nodes = db_stats['total_nodes']
            db_size_mb = db_stats['database_size_mb']
            hit_rate = cache_stats['hit_rate_percent']
            
            # Health thresholds
            if total_nodes > 10000 and db_size_mb > 100:
                performance_status = "needs_optimization"
            elif hit_rate < 50 and total_nodes > 1000:
                performance_status = "cache_inefficient"
            else:
                performance_status = "healthy"
            
            return {
                "performance_status": performance_status,
                "database_stats": db_stats,
                "cache_stats": cache_stats,
                "recommendations": _get_performance_recommendations(db_stats, cache_stats),
                "status": "healthy"
            }
    
    except Exception as e:
        logging.error(f"Error getting performance health: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get performance health",
                "message": str(e)
            }
        )

def _get_performance_recommendations(db_stats: Dict[str, Any], cache_stats: Dict[str, Any]) -> List[str]:
    """Get performance optimization recommendations."""
    recommendations = []
    
    total_nodes = db_stats['total_nodes']
    db_size_mb = db_stats['database_size_mb']
    hit_rate = cache_stats['hit_rate_percent']
    index_count = len(db_stats['indexes'])
    
    if total_nodes > 5000 and index_count < 5:
        recommendations.append("Consider creating additional database indexes for better query performance")
    
    if db_size_mb > 50:
        recommendations.append("Database size is growing - consider implementing data archiving for old records")
    
    if hit_rate < 30:
        recommendations.append("Cache hit rate is low - consider increasing cache size or optimizing cache keys")
    
    if total_nodes > 10000:
        recommendations.append("Large dataset detected - consider using streaming exports for data operations")
    
    if not recommendations:
        recommendations.append("Performance is optimal - no recommendations at this time")
    
    return recommendations
