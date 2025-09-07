"""
Test dictionary listing API contract.

Verifies that GET /api/v1/dictionary returns 200 with proper JSON shape,
not 500 due to missing table or query errors.
"""

import pytest
import requests


@pytest.fixture
def base_url():
    return "http://127.0.0.1:8000/api/v1"


def test_dictionary_list_returns_200_not_500(base_url):
    """Test that dictionary list returns 200, not 500."""

    response = requests.get(f"{base_url}/dictionary?limit=5")

    print(f"Dictionary list response status: {response.status_code}")
    print(f"Dictionary list response body: {response.text}")

    # Should not return 500 (internal server error)
    assert response.status_code != 500, \
        "Dictionary list returns 500 - likely missing table or query error"

    # Should return 200 (or possibly 404 if endpoint not implemented)
    if response.status_code == 404:
        pytest.skip("Dictionary endpoint not implemented (404)")
    else:
        assert response.status_code == 200


def test_dictionary_list_contract_when_working(base_url):
    """Test the full contract of dictionary list when it works."""

    response = requests.get(f"{base_url}/dictionary?limit=5")
    assert response.status_code == 200

    data = response.json()

    # Should be a dictionary with expected keys
    assert isinstance(data, dict)
    assert 'items' in data
    assert 'total' in data
    assert 'limit' in data
    assert 'offset' in data

    # Items should be a list
    assert isinstance(data['items'], list)

    # Numeric fields should be integers
    assert isinstance(data['total'], int)
    assert isinstance(data['limit'], int)
    assert isinstance(data['offset'], int)

    # Should respect limit parameter
    assert len(data['items']) <= data['limit']


def test_dictionary_list_with_query_parameters(base_url):
    """Test dictionary list with various query parameters."""

    # Test with different parameters
    params = {
        'type': 'node_label',
        'query': 'test',
        'limit': 10,
        'offset': 0,
        'sort': 'label',
        'direction': 'asc'
    }

    response = requests.get(f"{base_url}/dictionary", params=params)

    if response.status_code == 404:
        pytest.skip("Dictionary endpoint not implemented")
    elif response.status_code == 500:
        pytest.fail("Dictionary list fails with query parameters")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert 'items' in data


def test_dictionary_list_empty_response_handling(base_url):
    """Test that dictionary list handles empty results properly."""

    # Use a query that should return no results
    params = {'query': 'nonexistent_term_xyz123'}

    response = requests.get(f"{base_url}/dictionary", params=params)

    if response.status_code == 404:
        pytest.skip("Dictionary endpoint not implemented")
    elif response.status_code == 500:
        pytest.fail("Dictionary list fails with empty results")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert 'items' in data
    assert isinstance(data['items'], list)
    # Items list should be empty or contain no matches
    assert len(data['items']) == 0 or all(
        'nonexistent_term_xyz123' not in str(item).lower()
        for item in data['items']
    )
