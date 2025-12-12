"""
Integration tests for Dark Fiber Data API endpoints.

Tests the new type-specific data model API for dark fiber segments.

Prerequisites:
- A running NetBox instance with the cesnet_service_path_plugin installed
- An API token with appropriate permissions set in environment variables
- Valid Provider, Site, and Location IDs in the database

Run with:
    /home/albert/cesnet/netbox/venv/bin/python -m pytest tests/test_integration_dark_fiber_data_api.py -v
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

# Test data - adjust these IDs based on your NetBox instance
TEST_PROVIDER_ID = 57
TEST_SITE_A_ID = 221
TEST_LOCATION_A_ID = 140
TEST_SITE_B_ID = 6
TEST_LOCATION_B_ID = 15


@pytest.fixture(scope="module")
def base_segment():
    """Create a dark fiber segment WITHOUT technical data (two-step workflow)."""
    print("\n=== Creating Base Dark Fiber Segment (No Technical Data) ===")

    response = requests.post(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/",
        headers=HEADERS,
        json={
            "name": "Test Dark Fiber Segment for API",
            "status": "active",
            "segment_type": "dark_fiber",
            "provider": TEST_PROVIDER_ID,
            "site_a": TEST_SITE_A_ID,
            "location_a": TEST_LOCATION_A_ID,
            "site_b": TEST_SITE_B_ID,
            "location_b": TEST_LOCATION_B_ID,
        },
    )
    assert response.status_code == 201, f"Failed to create segment: {response.text}"

    segment_data = response.json()
    segment_id = segment_data["id"]
    print(f"Created segment with ID: {segment_id}")

    # Verify type_specific_data is None (no technical data yet)
    assert segment_data["type_specific_data"] is None

    yield segment_id

    # Cleanup
    print(f"\n=== Deleting Segment (ID: {segment_id}) ===")
    requests.delete(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{segment_id}/",
        headers=HEADERS,
    )


def test_create_dark_fiber_data(base_segment):
    """Test creating dark fiber technical data for a segment."""
    print(f"\n=== Creating Dark Fiber Technical Data for Segment {base_segment} ===")

    response = requests.post(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/dark-fiber-data/",
        headers=HEADERS,
        json={
            "segment_id": base_segment,
            "fiber_mode": "single_mode",
            "single_mode_subtype": "g652d",  # Lowercase
            "jacket_type": "outdoor",
            "fiber_attenuation_max": 0.25,
            "total_loss": 8.5,
            "total_length": 125.5,
            "number_of_fibers": 48,
            "connector_type_side_a": "lc_apc",  # Lowercase with underscore
            "connector_type_side_b": "sc_apc",  # Lowercase with underscore
        },
    )

    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.json()}")

    assert response.status_code == 201, f"Failed to create dark fiber data: {response.text}"

    data = response.json()

    # Verify returned data
    assert data["segment"]["id"] == base_segment
    assert data["segment"]["name"] == "Test Dark Fiber Segment for API"
    assert data["fiber_mode"] == "single_mode"
    assert data["single_mode_subtype"] == "g652d"
    assert data["jacket_type"] == "outdoor"
    assert float(data["fiber_attenuation_max"]) == 0.25
    assert float(data["total_loss"]) == 8.5
    assert float(data["total_length"]) == 125.5
    assert data["number_of_fibers"] == 48
    assert data["connector_type_side_a"] == "lc_apc"
    assert data["connector_type_side_b"] == "sc_apc"

    # Verify timestamps are present
    assert "created" in data
    assert "last_updated" in data


def test_retrieve_dark_fiber_data(base_segment):
    """Test retrieving dark fiber technical data."""
    print(f"\n=== Retrieving Dark Fiber Data for Segment {base_segment} ===")

    # The segment ID is the primary key for dark fiber data (OneToOne relationship)
    response = requests.get(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/dark-fiber-data/{base_segment}/",
        headers=HEADERS,
    )

    print(f"Response status: {response.status_code}")

    assert response.status_code == 200, f"Failed to retrieve dark fiber data: {response.text}"

    data = response.json()
    assert data["segment"]["id"] == base_segment
    assert data["fiber_mode"] == "single_mode"
    assert float(data["total_loss"]) == 8.5


def test_segment_includes_technical_data(base_segment):
    """Test that segment API includes type_specific_data field."""
    print(f"\n=== Verifying Segment Includes Technical Data (ID: {base_segment}) ===")

    response = requests.get(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{base_segment}/",
        headers=HEADERS,
    )

    assert response.status_code == 200

    data = response.json()

    # Verify type_specific_data is populated
    assert data["type_specific_data"] is not None
    assert data["type_specific_data"]["segment"]["id"] == base_segment
    assert data["type_specific_data"]["fiber_mode"] == "single_mode"
    assert float(data["type_specific_data"]["total_loss"]) == 8.5


def test_update_dark_fiber_data(base_segment):
    """Test updating dark fiber technical data."""
    print(f"\n=== Updating Dark Fiber Data for Segment {base_segment} ===")

    response = requests.patch(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/dark-fiber-data/{base_segment}/",
        headers=HEADERS,
        json={
            "total_loss": 7.2,
            "number_of_fibers": 96,
            "multimode_subtype": "",  # Clear multimode subtype
        },
    )

    print(f"Response status: {response.status_code}")

    assert response.status_code == 200, f"Failed to update dark fiber data: {response.text}"

    data = response.json()
    assert float(data["total_loss"]) == 7.2
    assert data["number_of_fibers"] == 96

    # Verify segment API reflects the update
    seg_response = requests.get(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{base_segment}/",
        headers=HEADERS,
    )
    seg_data = seg_response.json()
    assert float(seg_data["type_specific_data"]["total_loss"]) == 7.2


def test_delete_dark_fiber_data(base_segment):
    """Test deleting dark fiber technical data."""
    print(f"\n=== Deleting Dark Fiber Data for Segment {base_segment} ===")

    response = requests.delete(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/dark-fiber-data/{base_segment}/",
        headers=HEADERS,
    )

    print(f"Response status: {response.status_code}")

    assert response.status_code == 204, f"Failed to delete dark fiber data: {response.text}"

    # Verify data is deleted
    get_response = requests.get(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/dark-fiber-data/{base_segment}/",
        headers=HEADERS,
    )
    assert get_response.status_code == 404

    # Verify segment type_specific_data is now None
    seg_response = requests.get(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{base_segment}/",
        headers=HEADERS,
    )
    seg_data = seg_response.json()
    assert seg_data["type_specific_data"] is None


def test_cannot_create_duplicate_dark_fiber_data():
    """Test that creating duplicate dark fiber data for same segment fails."""
    print("\n=== Testing Duplicate Dark Fiber Data Prevention ===")

    # Create a segment
    seg_response = requests.post(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/",
        headers=HEADERS,
        json={
            "name": "Duplicate Test Segment",
            "status": "active",
            "segment_type": "dark_fiber",
            "provider": TEST_PROVIDER_ID,
            "site_a": TEST_SITE_A_ID,
            "site_b": TEST_SITE_B_ID,
        },
    )
    assert seg_response.status_code == 201
    segment_id = seg_response.json()["id"]

    try:
        # Create first dark fiber data
        response1 = requests.post(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/dark-fiber-data/",
            headers=HEADERS,
            json={
                "segment_id": segment_id,
                "fiber_mode": "single_mode",
                "total_loss": 5.0,
            },
        )
        assert response1.status_code == 201

        # Try to create second dark fiber data for same segment - should fail
        response2 = requests.post(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/dark-fiber-data/",
            headers=HEADERS,
            json={
                "segment_id": segment_id,
                "fiber_mode": "multimode",
                "total_loss": 6.0,
            },
        )

        print(f"Duplicate creation response status: {response2.status_code}")
        print(f"Duplicate creation response: {response2.json()}")

        # Should return 400 Bad Request with validation error
        assert response2.status_code == 400

    finally:
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{segment_id}/",
            headers=HEADERS,
        )


def test_fiber_mode_subtype_validation():
    """Test validation of fiber mode/subtype consistency."""
    print("\n=== Testing Fiber Mode/Subtype Validation ===")

    # Create a segment
    seg_response = requests.post(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/",
        headers=HEADERS,
        json={
            "name": "Validation Test Segment",
            "status": "active",
            "segment_type": "dark_fiber",
            "provider": TEST_PROVIDER_ID,
            "site_a": TEST_SITE_A_ID,
            "site_b": TEST_SITE_B_ID,
        },
    )
    assert seg_response.status_code == 201
    segment_id = seg_response.json()["id"]

    try:
        # Try to create dark fiber data with inconsistent mode/subtype
        # single_mode fiber with multimode subtype - should fail model validation
        response = requests.post(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/dark-fiber-data/",
            headers=HEADERS,
            json={
                "segment_id": segment_id,
                "fiber_mode": "single_mode",
                "multimode_subtype": "om3",  # Wrong! Should use single_mode_subtype
            },
        )

        print(f"Validation response status: {response.status_code}")
        print(f"Validation response: {response.json()}")

        # Should fail validation (400 Bad Request)
        assert response.status_code == 400

    finally:
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{segment_id}/",
            headers=HEADERS,
        )


def test_cascade_delete_on_segment_deletion():
    """Test that deleting a segment cascades to delete dark fiber data."""
    print("\n=== Testing Cascade Delete ===")

    # Create segment with dark fiber data
    seg_response = requests.post(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/",
        headers=HEADERS,
        json={
            "name": "Cascade Delete Test Segment",
            "status": "active",
            "segment_type": "dark_fiber",
            "provider": TEST_PROVIDER_ID,
            "site_a": TEST_SITE_A_ID,
            "site_b": TEST_SITE_B_ID,
        },
    )
    assert seg_response.status_code == 201
    segment_id = seg_response.json()["id"]

    # Create dark fiber data
    df_response = requests.post(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/dark-fiber-data/",
        headers=HEADERS,
        json={
            "segment_id": segment_id,
            "fiber_mode": "single_mode",
            "total_loss": 5.0,
        },
    )
    assert df_response.status_code == 201

    # Verify dark fiber data exists
    get_df_response = requests.get(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/dark-fiber-data/{segment_id}/",
        headers=HEADERS,
    )
    assert get_df_response.status_code == 200

    # Delete segment
    del_response = requests.delete(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{segment_id}/",
        headers=HEADERS,
    )
    assert del_response.status_code == 204

    # Verify dark fiber data is also deleted (cascade)
    get_df_after = requests.get(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/dark-fiber-data/{segment_id}/",
        headers=HEADERS,
    )
    assert get_df_after.status_code == 404
