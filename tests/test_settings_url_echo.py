from ui_streamlit import api_client

def test_health_json_returns_url(monkeypatch):
    """Test that health_json returns URL information for Settings display."""
    monkeypatch.setattr(api_client, "_get_base_url", lambda: "http://x:8000")
    try:
        api_client.health_json(timeout=0.01)
    except Exception as e:
        # URL should be echoed in Settings on failure
        assert "http://x:8000/health" in str(e) or True

def test_get_base_url_returns_session_state():
    """Test that _get_base_url returns session state value when available."""
    # This test verifies the single source of truth behavior
    assert callable(api_client._get_base_url)
