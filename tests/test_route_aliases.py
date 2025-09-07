from fastapi.testclient import TestClient
from api.app import app


def test_core_tree_endpoints_present():
    client = TestClient(app)

    r_stats = client.get('/api/v1/tree/stats')
    assert r_stats.status_code == 200
    body = r_stats.json()
    for k in ['nodes', 'roots', 'leaves', 'complete_paths', 'incomplete_parents']:
        assert k in body

    r_missing = client.get('/api/v1/tree/missing-slots-json?limit=1&offset=0')
    assert r_missing.status_code == 200
    m = r_missing.json()
    assert 'items' in m and 'total' in m

    r_export = client.get('/api/v1/tree/export-json?limit=1&offset=0')
    assert r_export.status_code == 200
    e = r_export.json()
    assert 'items' in e and 'total' in e

