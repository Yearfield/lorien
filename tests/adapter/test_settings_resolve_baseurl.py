import os
import importlib
from contextlib import contextmanager

@contextmanager
def patched_env(**kwargs):
    old = {k: os.environ.get(k) for k in kwargs}
    try:
        os.environ.update({k: v for k, v in kwargs.items() if v is not None})
        yield
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

def test_baseurl_env_fallback(monkeypatch):
    # simulate missing st.secrets
    monkeypatch.setattr("streamlit.secrets", {}, raising=False)
    with patched_env(API_BASE_URL="http://127.0.0.1:9000"):
        mod = importlib.import_module("ui_streamlit.settings")
        importlib.reload(mod)
        assert mod.get_api_base_url() == "http://127.0.0.1:9000"
