"""
Integration tests for Segment Contract Info API endpoints.
These tests cover creating, retrieving, updating, and deleting contract info
associated with service path segments.

Prerequisites:
- A running NetBox instance with the cesnet_service_path_plugin installed.
- An API token with appropriate permissions set in environment variables.
"""

import pytest
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_URL = os.getenv("NETBOX_URL")
API_TOKEN = os.getenv("API_TOKEN")
HEADERS = {"Authorization": f"Token {API_TOKEN}", "Content-Type": "application/json"}


@pytest.fixture(scope="module")
def contract_info_id():
    """Create contract info for segment 2 and return its ID."""
    print("\n=== Creating Contract Info for Segment 2 ===")

    response = requests.post(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segment-contract-info/",
        headers=HEADERS,
        json={
            "segment": 2,
            "recurring_charge": "5000.00",
            "charge_currency": "CZK",
            "non_recurring_charge": "10000.00",
            "notes": "Test via API",
        },
    )
    assert response.status_code == 201, f"Failed to create: {response.text}"

    created_id = response.json()["id"]
    print(f"Created contract info with ID: {created_id}")

    yield created_id

    # Cleanup: delete after all tests
    print(f"\n=== Deleting Contract Info (ID: {created_id}) ===")
    delete_response = requests.delete(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/contract-info/{created_id}/", headers=HEADERS
    )
    assert delete_response.status_code == 204, f"Failed to delete: {delete_response.text}"


def test_get_contract_info(contract_info_id):
    """Retrieve the created  info."""
    print(f"\n=== Getting Contract Info (ID: {contract_info_id}) ===")

    response = requests.get(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/contract-info/{contract_info_id}/",
        headers=HEADERS,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == contract_info_id
    assert data["segment"]["id"] == 2
    assert data["recurring_charge"] == 5000


def test_update_contract_info(contract_info_id):
    """Full update (PUT) of the contract info."""
    print(f"\n=== Updating Contract Info (PUT) (ID: {contract_info_id}) ===")

    response = requests.put(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/contract-info/{contract_info_id}/",
        headers=HEADERS,
        json={
            "segment": 2,
            "recurring_charge": "6000.00",
            "charge_currency": "EUR",
            "non_recurring_charge": "12000.00",
            "notes": "Updated contract info via API (PUT)",
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert data["recurring_charge"] == 6000
    assert data["charge_currency"] == "EUR"


def test_partial_update_contract_info(contract_info_id):
    """Partial update (PATCH) of specific fields."""
    print(f"\n=== Partial Update (PATCH) (ID: {contract_info_id}) ===")

    response = requests.patch(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/contract-info/{contract_info_id}/",
        headers=HEADERS,
        json={"recurring_charge": "7500.00", "notes": "Partially updated via API (PATCH)"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["recurring_charge"] == 7500.00
    assert data["notes"] == "Partially updated via API (PATCH)"


def test_get_segment_with_contract_info(contract_info_id):
    """Check that contract info appears in segment data."""
    print("\n=== Getting Segment 2 (should include contract_info) ===")

    response = requests.get(f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/2/", headers=HEADERS)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == 2
    # Check that contract info is linked
    assert "contract_info" in data or "segment_contract_info" in data
