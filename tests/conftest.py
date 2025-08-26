from __future__ import annotations
import os
import signal
import time
import pytest
from tests.utils.db import temp_db, start_api


@pytest.fixture
def temp_database():
    """
    Provides a fresh temporary DB per test and sets DB_PATH accordingly.
    """
    with temp_db() as db_path:
        yield db_path


@pytest.fixture
def api_server(temp_database):
    """
    Starts the FastAPI server (uvicorn) against the temp DB. Yields base_url.
    Tears down the process after the test.
    """
    proc, base_url = start_api(temp_database)
    try:
        yield base_url
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            # force kill if needed
            try:
                proc.send_signal(signal.SIGKILL)
            except Exception:
                pass
