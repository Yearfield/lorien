"""
Main entry point for the FastAPI application.
This file imports the app from app.py to maintain compatibility.
"""

from .app import app

# Export the app for uvicorn
__all__ = ["app"]