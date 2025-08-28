from __future__ import annotations
import os
import sqlite3
import tempfile
import time
import subprocess
from contextlib import contextmanager
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import json
import socket


def _apply_schema(db_path: str, schema_path: str) -> None:
    print(f"[DEBUG] _apply_schema: Applying schema to {db_path}")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(schema_sql)
        conn.commit()
        print(f"[DEBUG] _apply_schema: Schema applied and committed, DB size: {os.path.getsize(db_path)} bytes")
    finally:
        conn.close()
        print(f"[DEBUG] _apply_schema: Connection closed")


@contextmanager
def temp_db(schema_rel_path: str = "storage/schema.sql"):
    """
    Creates a temporary DB, applies schema.sql, and sets DB_PATH env var for the duration.
    Yields the db_path string.
    """
    tmpdir = tempfile.TemporaryDirectory()
    old_env = None
    try:
        db_path = os.path.join(tmpdir.name, "app.db")
        repo_root = Path(__file__).resolve().parents[2]
        schema_path = str((repo_root / schema_rel_path).resolve())
        
        print(f"[DEBUG] temp_db: Creating DB at absolute path: {os.path.abspath(db_path)}")
        print(f"[DEBUG] temp_db: Schema path: {schema_path}")
        
        _apply_schema(db_path, schema_path)
        
        print(f"[DEBUG] temp_db: Schema applied, DB size: {os.path.getsize(db_path)} bytes")
        print(f"[DEBUG] temp_db: Setting DB_PATH env var to: {db_path}")

        old_env = os.environ.get("DB_PATH")
        os.environ["DB_PATH"] = db_path
        yield db_path
    finally:
        # restore env
        if old_env is None:
            os.environ.pop("DB_PATH", None)
        else:
            os.environ["DB_PATH"] = old_env
        tmpdir.cleanup()


def _find_free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def _wait_for_health(base_url: str, timeout_s: float = 10.0) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            req = Request(base_url + "/api/v1/health", headers={"Accept": "application/json"})
            with urlopen(req, timeout=0.5) as resp:
                if resp.status == 200:
                    # sanity parse
                    _ = json.loads(resp.read().decode("utf-8"))
                    return
        except (URLError, HTTPError, TimeoutError, ConnectionError):
            pass
        time.sleep(0.1)
    raise RuntimeError(f"API /health not responding at {base_url}")


def start_api(db_path: str, host: str = "127.0.0.1") -> tuple[subprocess.Popen, str]:
    """
    Starts uvicorn in a subprocess bound to a free port, with DB_PATH set.
    Returns (proc, base_url). Caller is responsible to terminate proc.
    """
    port = _find_free_port()
    env = os.environ.copy()
    env["DB_PATH"] = db_path
    env.setdefault("APP_VERSION", "test-e2e")
    proc = subprocess.Popen(
        ["python", "-m", "uvicorn", "api.app:app", "--host", host, "--port", str(port), "--log-level", "warning"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    base_url = f"http://{host}:{port}"
    try:
        _wait_for_health(base_url, timeout_s=12.0)
    except Exception:
        # surface some logs to help debugging
        out = ""
        try:
            if proc.stdout:
                out = "".join(proc.stdout.readlines()[-100:])
        except Exception:
            pass
        proc.terminate()
        raise RuntimeError(f"Failed to start API at {base_url}\n--- logs ---\n{out}")
    return proc, base_url
