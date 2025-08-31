from __future__ import annotations
import io
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
import streamlit as st
from ui_streamlit.settings import get_api_base_url
from typing import Dict, List, Any, Optional, Tuple
import time
import os
import json

HEADERS_JSON = {"Accept": "application/json", "Content-Type": "application/json"}

# Simple in-memory cache with TTL
class SimpleCache:
    def __init__(self, ttl_seconds: int = 300):  # 5 minutes default
        self.cache: Dict[str, tuple[Any, float]] = {}
        self.ttl = ttl_seconds
    
    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        self.cache[key] = (value, time.time())
    
    def invalidate(self, key: str):
        if key in self.cache:
            del self.cache[key]
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate all keys that start with the pattern."""
        keys_to_remove = [k for k in self.cache.keys() if k.startswith(pattern)]
        for key in keys_to_remove:
            del self.cache[key]

# Global cache instance
_cache = SimpleCache()

def _url(path: str) -> str:
    base = get_api_base_url()
    path = path if path.startswith("/") else "/" + path
    return base + path

def _cache_key(prefix: str, *args, **kwargs) -> str:
    """Generate a cache key from prefix and arguments."""
    key_parts = [prefix]
    if args:
        key_parts.extend(str(arg) for arg in args)
    if kwargs:
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")
    return ":".join(key_parts)

def _get_base_url() -> str:
    """Single source of truth for base URL (Settings populates this)"""
    return st.session_state.get("API_BASE_URL") or os.getenv("LORIEN_API_BASE", "http://localhost:8000")

def health_json(timeout=3):
    """Check connectivity via /health endpoint only - single source of truth"""
    base = _get_base_url()
    try:
        r = requests.get(f"{base}/health", timeout=timeout)
        r.raise_for_status()
        return r.json(), r.status_code, f"{base}/health"
    except requests.RequestException as e:
        # Return error details without changing global connection state
        return None, getattr(e.response, 'status_code', 0) if hasattr(e, 'response') else 0, f"{base}/health"

def get_json(endpoint, timeout=10):
    """Get JSON from API endpoint"""
    base = _get_base_url()
    r = requests.get(f"{base}{endpoint}", timeout=timeout)
    r.raise_for_status()
    return r.json()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.2, min=0.2, max=2))
def get_next_incomplete_parent() -> dict | None:
    r = requests.get(_url("/tree/next-incomplete-parent"), timeout=8, headers=HEADERS_JSON)
    if r.status_code == 204 or not r.content:
        return None
    r.raise_for_status()
    return r.json()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.2, min=0.2, max=2))
def get_children(parent_id: int, use_cache: bool = True) -> list[dict]:
    """Get children for a parent with optional caching."""
    if use_cache:
        cache_key = _cache_key("children", parent_id)
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached
    
    r = requests.get(_url(f"/tree/{parent_id}/children"), timeout=8, headers=HEADERS_JSON)
    r.raise_for_status()
    result = r.json()
    
    if use_cache:
        cache_key = _cache_key("children", parent_id)
        _cache.set(cache_key, result)
    
    return result

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.2, min=0.2, max=2))
def upsert_children(parent_id: int, children: list[dict]) -> dict:
    # children: [{"slot":1..5,"label":"..."}]
    r = requests.post(_url(f"/tree/{parent_id}/children"), json={"children": children}, timeout=12, headers=HEADERS_JSON)
    r.raise_for_status()
    result = r.json() if r.content else {}
    
    # Invalidate cache for this parent's children
    _cache.invalidate_pattern(f"children:{parent_id}")
    
    return result

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.2, min=0.2, max=2))
def get_triage(node_id: int, use_cache: bool = True) -> dict:
    """Get triage for a node with optional caching."""
    if use_cache:
        cache_key = _cache_key("triage", node_id)
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached
    
    r = requests.get(_url(f"/triage/{node_id}"), timeout=8, headers=HEADERS_JSON)
    r.raise_for_status()
    result = r.json()
    
    if use_cache:
        cache_key = _cache_key("triage", node_id)
        _cache.set(cache_key, result)
    
    return result

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.2, min=0.2, max=2))
def put_triage(node_id: int, triage: dict) -> dict:
    r = requests.put(_url(f"/triage/{node_id}"), json=triage, timeout=12, headers=HEADERS_JSON)
    r.raise_for_status()
    result = r.json()
    
    # Invalidate cache for this node's triage
    _cache.invalidate(f"triage:{node_id}")
    
    return result

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.2, min=0.2, max=2))
def flags_search(q: str, use_cache: bool = True) -> dict:
    """Search flags with optional caching."""
    if use_cache:
        cache_key = _cache_key("flags_search", q)
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached
    
    r = requests.get(_url(f"/flags/search"), params={"q": q}, timeout=8, headers=HEADERS_JSON)
    r.raise_for_status()
    result = r.json()
    
    if use_cache:
        cache_key = _cache_key("flags_search", q)
        _cache.set(cache_key, result)
    
    return result

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.2, min=0.2, max=2))
def flags_assign(node_id: int, red_flag_name: str, user: str | None = None, cascade: bool = False) -> dict:
    payload = {"node_id": node_id, "red_flag_name": red_flag_name, "cascade": cascade}
    if user:
        payload["user"] = user
    r = requests.post(_url("/flags/assign"), json=payload, timeout=8, headers=HEADERS_JSON)
    r.raise_for_status()
    result = r.json() if r.content else {}
    
    # Invalidate relevant caches
    _cache.invalidate_pattern("flags_search")
    
    return result

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.2, min=0.2, max=2))
def calc_export_csv() -> tuple[str, bytes]:
    r = requests.get(_url("/calc/export"), timeout=30, headers={"Accept": "text/csv"})
    r.raise_for_status()
    filename = "export.csv"
    disp = r.headers.get("content-disposition", "")
    # best-effort filename parse
    for part in disp.split(";"):
        part = part.strip()
        if part.lower().startswith("filename="):
            filename = part.split("=",1)[1].strip('"')
            break
    return filename, r.content

def post_json(endpoint, data, timeout=10):
    """Post JSON to API endpoint"""
    base = _get_base_url()
    r = requests.post(f"{base}{endpoint}", json=data, timeout=timeout)
    r.raise_for_status()
    return r.json()

def post_file(endpoint, files, timeout=30):
    """Post file to API endpoint"""
    base = _get_base_url()
    r = requests.post(f"{base}{endpoint}", files=files, timeout=timeout)
    r.raise_for_status()
    return r.json()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.2, min=0.2, max=2))
def get_csv_export(path: str) -> str:
    """GET CSV export and return content as string."""
    r = requests.get(_url(path), timeout=30)
    r.raise_for_status()
    return r.text

def put_json(endpoint, data, timeout=10):
    """Put JSON to API endpoint"""
    base = _get_base_url()
    r = requests.put(f"{base}{endpoint}", json=data, timeout=timeout)
    r.raise_for_status()
    return r.json()

def delete_json(endpoint, timeout=10):
    """Delete from API endpoint"""
    base = _get_base_url()
    r = requests.delete(f"{base}{endpoint}", timeout=timeout)
    r.raise_for_status()
    return r.json()

def clear_cache():
    """Clear all cached data."""
    global _cache
    _cache = SimpleCache()

def get_cache_stats() -> dict:
    """Get cache statistics for debugging."""
    return {
        "cache_size": len(_cache.cache),
        "ttl_seconds": _cache.ttl
    }
