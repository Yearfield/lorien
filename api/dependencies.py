"""
Dependency injection for FastAPI application.
"""

import sqlite3
from typing import Generator
from fastapi import Depends, HTTPException, status
from contextlib import contextmanager

from storage.sqlite import SQLiteRepository
from core.models import Node, Triaging


def get_repository() -> SQLiteRepository:
    """
    Get SQLite repository instance.
    
    Returns:
        SQLiteRepository: Configured repository instance
    """
    return SQLiteRepository()


import logging

logger = logging.getLogger(__name__)

@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """
    Get database connection with proper configuration.
    
    Yields:
        sqlite3.Connection: Configured database connection
        
    Note:
        Connection is automatically closed when context exits.
    """
    repo = get_repository()
    conn = repo._get_connection()
    try:
        # Initialize connection with required pragmas on every request
        logger.debug("Enabling WAL mode...")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        logger.debug("WAL mode enabled.")
        yield conn
    finally:
        conn.close()


def validate_node_exists(node_id: int, repo: SQLiteRepository = Depends(get_repository)) -> Node:
    """
    Validate that a node exists and return it.
    
    Args:
        node_id: ID of the node to validate
        repo: Repository instance
        
    Returns:
        Node: The validated node
        
    Raises:
        HTTPException: If node doesn't exist
    """
    node = repo.get_node(node_id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node with ID {node_id} not found"
        )
    return node


def validate_parent_exists(parent_id: int, repo: SQLiteRepository = Depends(get_repository)) -> Node:
    """
    Validate that a parent node exists and return it.
    
    Args:
        parent_id: ID of the parent node to validate
        repo: Repository instance
        
    Returns:
        Node: The validated parent node
        
    Raises:
        HTTPException: If parent doesn't exist
    """
    parent = validate_node_exists(parent_id, repo)
    
    # Additional validation: ensure it's not a leaf node (depth < 5)
    if parent.depth >= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Node {parent_id} is a leaf node and cannot have children"
        )
    
    return parent


def validate_triage_exists(node_id: int, repo: SQLiteRepository = Depends(get_repository)) -> Triaging:
    """
    Validate that triage exists for a node and return it.
    
    Args:
        node_id: ID of the node
        repo: Repository instance
        
    Returns:
        Triaging: The triage data
        
    Raises:
        HTTPException: If triage doesn't exist
    """
    triage = repo.get_triage(node_id)
    if not triage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Triage not found for node {node_id}"
        )
    return triage
