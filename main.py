#!/usr/bin/env python3
"""
Main entry point for the Decision Tree API server.
"""

import uvicorn
import os
import logging
from api.app import app
from core.version import __version__

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Get configuration from environment variables
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    logger.info("Starting Decision Tree API server...")
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info(f"Reload: {reload}")
    logger.info(f"Version: {__version__}")
    logger.info(f"Docs: http://{host}:{port}/docs")
    logger.info(f"API v1 Health: http://{host}:{port}/api/v1/health")
    
    # Start the server
    uvicorn.run(
        "api.app:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
