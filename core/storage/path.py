from __future__ import annotations
import os
import sys
from pathlib import Path
from typing import Tuple

DEFAULT_APP_NAME = "lorien"

def _platform_paths(app_name: str) -> Tuple[Path, Path]:
    """
    Returns (data_dir, db_path) for the current OS.
    - Linux: ~/.local/share/{app}/app.db
    - macOS: ~/Library/Application Support/{app}/app.db
    - Windows: %APPDATA%\\{app}\\app.db
    """
    home = Path.home()
    if sys.platform.startswith("linux"):
        data_dir = home / ".local" / "share" / app_name
    elif sys.platform == "darwin":
        data_dir = home / "Library" / "Application Support" / app_name
    elif os.name == "nt":
        appdata = os.getenv("APPDATA") or str(home / "AppData" / "Roaming")
        data_dir = Path(appdata) / app_name
    else:
        data_dir = home / f".{app_name}"
    return data_dir, (data_dir / "app.db")

def get_db_path(app_name: str = DEFAULT_APP_NAME) -> Path:
    """
    Env-first resolution:
      1) DB_PATH env -> absolute resolved
      2) OS-appropriate app-data dir
    Ensures parent directory exists.
    """
    env_path = os.environ.get("DB_PATH")
    if env_path:
        p = Path(env_path).expanduser().resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        return p
    data_dir, db = _platform_paths(app_name)
    data_dir.mkdir(parents=True, exist_ok=True)
    return db.resolve()
