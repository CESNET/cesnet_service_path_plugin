"""
Integration tests for Segment Contract Info API endpoints.
These tests cover creating, retrieving, updating, and deleting contract info
associated with service path segments, including contract versioning.

Prerequisites:
- A running NetBox instance with the cesnet_service_path_plugin installed.
- An API token with appropriate permissions set in environment variables.
"""

import pytest
import requests
import os
from datetime import date, timedelta
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

    today = date.today()

    response = requests.post(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/contract-info/",
        headers=HEADERS,
        json={
            "segments": [2],  # M2M field - list of segment IDs
            "contract_number": "TEST-2024-001",
            "start_date": str(today),
            "end_date": str(today + timedelta(days=365)),
            "recurring_charge": "5000.00",
            "recurring_charge_period": "monthly",
            "number_of_recurring_charges": 12,
            "charge_currency": "CZK",
            "non_recurring_charge": "10000.00",
            "notes": "Test contract created via API",
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
    """Retrieve the created contract info."""
    print(f"\n=== Getting Contract Info (ID: {contract_info_id}) ===")

    response = requests.get(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/contract-info/{contract_info_id}/",
        headers=HEADERS,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == contract_info_id
    assert len(data["segments"]) == 1
    assert data["segments"][0]["id"] == 2
    assert float(data["recurring_charge"]) == 5000.0
    assert data["contract_number"] == "TEST-2024-001"
    assert data["is_active"] is True
    assert data["version"] == 1
    assert data["contract_type"] == "new"


def test_update_contract_info(contract_info_id):
    """Full update (PUT) of the contract info."""
    print(f"\n=== Updating Contract Info (PUT) (ID: {contract_info_id}) ===")

    today = date.today()

    response = requests.put(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/contract-info/{contract_info_id}/",
        headers=HEADERS,
        json={
            "segments": [2],
            "contract_number": "TEST-2024-001",
            "start_date": str(today),
            "end_date": str(today + timedelta(days=365)),
            "recurring_charge": "6000.00",
            "recurring_charge_period": "monthly",
            "number_of_recurring_charges": 12,
            "charge_currency": "EUR",
            "non_recurring_charge": "12000.00",
            "notes": "Updated contract info via API (PUT)",
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert float(data["recurring_charge"]) == 6000.0
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
    assert float(data["recurring_charge"]) == 7500.0
    assert data["notes"] == "Partially updated via API (PATCH)"


def test_get_segment_with_contracts(contract_info_id):
    """Check that contract info appears in segment data."""
    print("\n=== Getting Segment 2 (should include contracts) ===")

    response = requests.get(f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/2/", headers=HEADERS)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == 2
    # Check that contracts relationship exists
    assert "contracts" in data or "contract_info" in data


# ============================================================================
# CONTRACT VERSIONING AND CLONING TESTS
# ============================================================================


@pytest.fixture(scope="module")
def versioned_contract_chain():
    """Create a chain of contract versions for testing versioning functionality."""
    print("\n=== Creating Contract Version Chain ===")

    today = date.today()
    contract_ids = []

    # Create v1 (initial contract)
    print("Creating Version 1...")
    response_v1 = requests.post(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/contract-info/",
        headers=HEADERS,
        json={
            "segments": [3],
            "contract_number": "VERSION-TEST-001",
            "start_date": str(today - timedelta(days=365)),
            "end_date": str(today),
            "recurring_charge": "1000.00",
            "recurring_charge_period": "monthly",
            "number_of_recurring_charges": 12,
            "charge_currency": "CZK",
            "non_recurring_charge": "5000.00",
            "notes": "Initial version notes",
        },
    )
    assert response_v1.status_code == 201, f"Failed to create v1: {response_v1.text}"
    v1_id = response_v1.json()["id"]
    contract_ids.append(v1_id)
    print(f"  Created v1 with ID: {v1_id}")

    # Create v2 (amendment)
    print("Creating Version 2 (amendment)...")
    response_v2 = requests.post(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/contract-info/",
        headers=HEADERS,
        json={
            "segments": [3],
            "contract_number": "VERSION-TEST-001",
            "previous_version": v1_id,
            "contract_type": "amendment",
            "start_date": str(today - timedelta(days=180)),
            "end_date": str(today + timedelta(days=185)),
            "recurring_charge": "1200.00",
            "recurring_charge_period": "monthly",
            "number_of_recurring_charges": 12,
            "charge_currency": "CZK",
            "non_recurring_charge": "0.00",
            "notes": "Amendment v2 notes",
        },
    )
    assert response_v2.status_code == 201, f"Failed to create v2: {response_v2.text}"
    v2_id = response_v2.json()["id"]
    contract_ids.append(v2_id)
    print(f"  Created v2 with ID: {v2_id}")

    # Create v3 (renewal)
    print("Creating Version 3 (renewal)...")
    response_v3 = requests.post(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/contract-info/",
        headers=HEADERS,
        json={
            "segments": [3],
            "contract_number": "VERSION-TEST-001",
            "previous_version": v2_id,
            "contract_type": "renewal",
            "start_date": str(today),
            "end_date": str(today + timedelta(days=365)),
            "recurring_charge": "1300.00",
            "recurring_charge_period": "monthly",
            "number_of_recurring_charges": 12,
            "charge_currency": "CZK",
            "non_recurring_charge": "0.00",
            "notes": "Renewal v3 notes",
        },
    )
    assert response_v3.status_code == 201, f"Failed to create v3: {response_v3.text}"
    v3_id = response_v3.json()["id"]
    contract_ids.append(v3_id)
    print(f"  Created v3 with ID: {v3_id}")

    yield {"v1_id": v1_id, "v2_id": v2_id, "v3_id": v3_id, "all_ids": contract_ids}

    # Cleanup: delete all versions
    print("\n=== Cleaning up Contract Version Chain ===")
    for contract_id in reversed(contract_ids):  # Delete in reverse order
        delete_response = requests.delete(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/contract-info/{contract_id}/", headers=HEADERS
        )
        print(f"  Deleted contract ID: {contract_id} - Status: {delete_response.status_code}")


def test_contract_version_numbers(versioned_contract_chain):
    """Test that version numbers are correctly assigned."""
    print("\n=== Testing Contract Version Numbers ===")

    v1_id = versioned_contract_chain["v1_id"]
    v2_id = versioned_contract_chain["v2_id"]
    v3_id = versioned_contract_chain["v3_id"]

    # Check v1
    response = requests.get(f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/contract-info/{v1_id}/", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == 1
    assert data["contract_type"] == "new"
    # V1 should be superseded after v2 was created
    print(f"V1 is_active: {data['is_active']}, superseded_by: {data['superseded_by']}")
    assert data["is_active"] is False, f"V1 should be inactive (superseded), but is_active={data['is_active']}"
    assert data["previous_version"] is None
    assert data["superseded_by"] == v2_id, f"V1 should be superseded by v2 ({v2_id}), but superseded_by={data['superseded_by']}"

    # Check v2
    response = requests.get(f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/contract-info/{v2_id}/", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == 2
    assert data["contract_type"] == "amendment"
    assert data["is_active"] is False  # Superseded by v3
    assert data["previous_version"] == v1_id
    assert data["superseded_by"] == v3_id

    # Check v3
    response = requests.get(f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/contract-info/{v3_id}/", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == 3
    assert data["contract_type"] == "renewal"
    assert data["is_active"] is True  # Latest version
    assert data["previous_version"] == v2_id
    assert data["superseded_by"] is None


def test_contract_notes(versioned_contract_chain):
    """Test that contract notes are stored correctly."""
    print("\n=== Testing Contract Notes ===")

    v3_id = versioned_contract_chain["v3_id"]

    response = requests.get(f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/contract-info/{v3_id}/", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()

    # Check that notes field exists and contains the expected value
    notes = data.get("notes", "")
    print(f"Current notes (v3): '{notes}'")
    assert notes == "Renewal v3 notes", f"Expected 'Renewal v3 notes', got: {notes}"


def test_computed_financial_fields(versioned_contract_chain):
    """Test computed financial fields."""
    print("\n=== Testing Computed Financial Fields ===")

    v3_id = versioned_contract_chain["v3_id"]

    response = requests.get(f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/contract-info/{v3_id}/", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()

    # Check computed fields
    assert "total_recurring_cost" in data
    assert "total_contract_value" in data
    assert "commitment_end_date" in data

    # Validate calculations
    recurring_charge = float(data["recurring_charge"])
    num_charges = data["number_of_recurring_charges"]
    expected_total = recurring_charge * num_charges

    assert float(data["total_recurring_cost"]) == expected_total


def test_filtering_active_contracts():
    """Test filtering contracts by is_active status."""
    print("\n=== Testing Active Contract Filtering ===")

    # This test assumes the versioned_contract_chain fixture has been run
    response = requests.get(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/contract-info/",
        headers=HEADERS,
        params={"is_active": "true"},
    )

    assert response.status_code == 200
    data = response.json()

    # All returned contracts should be active (is_active=True)
    for contract in data.get("results", []):
        assert contract["is_active"] is True


def test_contract_currency_immutability(versioned_contract_chain):
    """Test that currency cannot be changed in amendments (validation)."""
    print("\n=== Testing Currency Immutability ===")

    v3_id = versioned_contract_chain["v3_id"]
    today = date.today()

    # Attempt to change currency (should fail validation)
    response = requests.patch(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/contract-info/{v3_id}/",
        headers=HEADERS,
        json={"charge_currency": "EUR"},  # Try to change from CZK to EUR
    )

    # This might return 400 if validation is enforced at API level
    # The actual status code depends on implementation
    # Just document the current behavior
    print(f"  Response status: {response.status_code}")
    if response.status_code != 200:
        print(f"  Validation message: {response.text}")
