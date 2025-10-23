"""
Integration tests for Segment Financial Info API endpoints.
These tests cover creating, retrieving, updating, and deleting financial info
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
def financial_info_id():
    """Create financial info for segment 2 and return its ID."""
    print("\n=== Creating Financial Info for Segment 2 ===")

    response = requests.post(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segment-financial-info/",
        headers=HEADERS,
        json={
            "segment": 2,
            "monthly_charge": "5000.00",
            "charge_currency": "CZK",
            "non_recurring_charge": "10000.00",
            "commitment_period_months": 24,
            "notes": "Test via API",
        },
    )
    assert response.status_code == 201, f"Failed to create: {response.text}"

    created_id = response.json()["id"]
    print(f"Created financial info with ID: {created_id}")

    yield created_id

    # Cleanup: delete after all tests
    print(f"\n=== Deleting Financial Info (ID: {created_id}) ===")
    delete_response = requests.delete(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segment-financial-info/{created_id}/", headers=HEADERS
    )
    assert delete_response.status_code == 204, f"Failed to delete: {delete_response.text}"


def test_get_financial_info(financial_info_id):
    """Retrieve the created financial info."""
    print(f"\n=== Getting Financial Info (ID: {financial_info_id}) ===")

    response = requests.get(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segment-financial-info/{financial_info_id}/",
        headers=HEADERS,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == financial_info_id
    assert data["segment"]["id"] == 2
    assert data["monthly_charge"] == 5000


def test_update_financial_info(financial_info_id):
    """Full update (PUT) of the financial info."""
    print(f"\n=== Updating Financial Info (PUT) (ID: {financial_info_id}) ===")

    response = requests.put(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segment-financial-info/{financial_info_id}/",
        headers=HEADERS,
        json={
            "segment": 2,
            "monthly_charge": "6000.00",
            "charge_currency": "EUR",
            "non_recurring_charge": "12000.00",
            "commitment_period_months": 36,
            "notes": "Updated financial info via API (PUT)",
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert data["monthly_charge"] == 6000
    assert data["charge_currency"] == "EUR"


def test_partial_update_financial_info(financial_info_id):
    """Partial update (PATCH) of specific fields."""
    print(f"\n=== Partial Update (PATCH) (ID: {financial_info_id}) ===")

    response = requests.patch(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segment-financial-info/{financial_info_id}/",
        headers=HEADERS,
        json={"monthly_charge": "7500.00", "notes": "Partially updated via API (PATCH)"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["monthly_charge"] == 7500.00
    assert data["notes"] == "Partially updated via API (PATCH)"


def test_get_segment_with_financial_info(financial_info_id):
    """Check that financial info appears in segment data."""
    print("\n=== Getting Segment 2 (should include financial_info) ===")

    response = requests.get(f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/2/", headers=HEADERS)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == 2
    # Check that financial info is linked
    assert "financial_info" in data or "segment_financial_info" in data
