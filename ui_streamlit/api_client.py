from __future__ import annotations
import io
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
import streamlit as st
from .settings import get_api_base_url

HEADERS_JSON = {"Accept": "application/json", "Content-Type": "application/json"}

def _url(path: str) -> str:
    base = get_api_base_url()
    path = path if path.startswith("/") else "/" + path
    return base + path

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.2, min=0.2, max=2))
def get_health() -> dict:
    r = requests.get(_url("/health"), timeout=5)
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
def get_children(parent_id: int) -> list[dict]:
    r = requests.get(_url(f"/tree/{parent_id}/children"), timeout=8, headers=HEADERS_JSON)
    r.raise_for_status()
    return r.json()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.2, min=0.2, max=2))
def upsert_children(parent_id: int, children: list[dict]) -> dict:
    # children: [{"slot":1..5,"label":"..."}]
    r = requests.post(_url(f"/tree/{parent_id}/children"), json={"children": children}, timeout=12, headers=HEADERS_JSON)
    r.raise_for_status()
    return r.json() if r.content else {}

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.2, min=0.2, max=2))
def get_triage(node_id: int) -> dict:
    r = requests.get(_url(f"/triage/{node_id}"), timeout=8, headers=HEADERS_JSON)
    r.raise_for_status()
    return r.json()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.2, min=0.2, max=2))
def put_triage(node_id: int, triage: dict) -> dict:
    r = requests.put(_url(f"/triage/{node_id}"), json=triage, timeout=12, headers=HEADERS_JSON)
    r.raise_for_status()
    return r.json()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.2, min=0.2, max=2))
def flags_search(q: str) -> list[dict]:
    r = requests.get(_url(f"/flags/search"), params={"q": q}, timeout=8, headers=HEADERS_JSON)
    r.raise_for_status()
    return r.json()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.2, min=0.2, max=2))
def flags_assign(node_id: int, red_flag_name: str) -> dict:
    r = requests.post(_url("/flags/assign"), json={"node_id": node_id, "red_flag_name": red_flag_name}, timeout=8, headers=HEADERS_JSON)
    r.raise_for_status()
    return r.json()

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
