"""
Test dictionary CRUD operations and normalize endpoint.
"""

from fastapi.testclient import TestClient
from api.app import app

c = TestClient(app)

def test_dictionary_create_list_normalize_and_uniqueness():
    import time
    unique_suffix = str(int(time.time()))  # Make test terms unique

    # create
    term = f"Test Fever {unique_suffix}"
    r = c.post("/api/v1/dictionary", json={"type": "node_label", "term": f"  {term}  "})
    assert r.status_code == 200
    j = r.json()
    assert j["normalized"] == term.lower()

    # duplicate (same normalized) -> 422
    r2 = c.post("/api/v1/dictionary", json={"type": "node_label", "term": term})
    assert r2.status_code == 422
    assert "duplicate" in r2.json()["detail"][0]["msg"].lower()

    # list with query
    lr = c.get("/api/v1/dictionary", params={"type": "node_label", "query": term.lower()[:3]})
    assert lr.status_code == 200
    assert lr.json()["total"] >= 1
    assert any(item["normalized"] == term.lower() for item in lr.json()["items"])

    # normalize endpoint (hit existing)
    nr = c.get("/api/v1/dictionary/normalize", params={"type": "node_label", "term": term.upper()})
    assert nr.status_code == 200
    assert nr.json()["normalized"] == term.lower()

    # normalize endpoint (fallback)
    nr2 = c.get("/api/v1/dictionary/normalize", params={"type": "node_label", "term": f"New Term {unique_suffix}"})
    assert nr2.status_code == 200
    assert nr2.json()["normalized"] == f"new term {unique_suffix}"


def test_dictionary_update_and_delete():
    import time
    unique_suffix = str(int(time.time()))  # Make test terms unique

    # create term
    term = f"Temperature {unique_suffix}"
    r = c.post("/api/v1/dictionary", json={"type": "vital_measurement", "term": term})
    assert r.status_code == 200
    term_id = r.json()["id"]

    # update term
    updated_term = f"Body Temperature {unique_suffix}"
    ur = c.put(f"/api/v1/dictionary/{term_id}", json={"term": updated_term, "hints": "Core temp"})
    assert ur.status_code == 200
    assert ur.json()["term"] == updated_term
    assert ur.json()["hints"] == "Core temp"

    # delete term
    dr = c.delete(f"/api/v1/dictionary/{term_id}")
    assert dr.status_code == 200

    # verify deleted
    gr = c.get(f"/api/v1/dictionary/{term_id}")
    assert gr.status_code == 404


def test_dictionary_pagination():
    import time
    unique_suffix = str(int(time.time()))  # Make test terms unique

    # create multiple terms
    created_ids = []
    for i in range(5):
        r = c.post("/api/v1/dictionary", json={"type": "outcome_template", "term": f"Template {i} {unique_suffix}"})
        assert r.status_code == 200
        created_ids.append(r.json()["id"])

    # test pagination
    pr = c.get("/api/v1/dictionary", params={"type": "outcome_template", "query": unique_suffix, "limit": 2, "offset": 1})
    assert pr.status_code == 200
    data = pr.json()
    assert len(data["items"]) == 2
    assert data["total"] >= 5
    assert data["limit"] == 2
    assert data["offset"] == 1

    # cleanup
    for term_id in created_ids:
        c.delete(f"/api/v1/dictionary/{term_id}")


def test_dictionary_types_validation():
    import time
    unique_suffix = str(int(time.time()))  # Make test terms unique

    # valid types
    for t in ["vital_measurement", "node_label", "outcome_template"]:
        r = c.post("/api/v1/dictionary", json={"type": t, "term": f"Test {t} {unique_suffix}"})
        assert r.status_code == 200

    # invalid type
    r = c.post("/api/v1/dictionary", json={"type": "invalid_type", "term": f"Test invalid {unique_suffix}"})
    assert r.status_code == 422
