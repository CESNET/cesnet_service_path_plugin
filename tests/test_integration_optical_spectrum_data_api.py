"""
Integration tests for Optical Spectrum Data API endpoints.

Tests the new type-specific data model API for optical spectrum segments.

Prerequisites:
- A running NetBox instance with the cesnet_service_path_plugin installed
- An API token with appropriate permissions set in environment variables
- Valid Provider, Site, and Location IDs in the database

Run with:
    /home/albert/cesnet/netbox/venv/bin/python -m pytest tests/test_integration_optical_spectrum_data_api.py -v
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

# Test data
TEST_PROVIDER_ID = 57
TEST_SITE_A_ID = 221
TEST_LOCATION_A_ID = 140
TEST_SITE_B_ID = 6
TEST_LOCATION_B_ID = 15


@pytest.fixture(scope="module")
def base_segment():
    """Create an optical spectrum segment WITHOUT technical data."""
    print("\n=== Creating Base Optical Spectrum Segment (No Technical Data) ===")

    response = requests.post(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/",
        headers=HEADERS,
        json={
            "name": "Test Optical Spectrum Segment for API",
            "status": "active",
            "segment_type": "optical_spectrum",
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


def test_create_optical_spectrum_data(base_segment):
    """Test creating optical spectrum technical data for a segment."""
    print(f"\n=== Creating Optical Spectrum Technical Data for Segment {base_segment} ===")

    response = requests.post(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/optical-spectrum-data/",
        headers=HEADERS,
        json={
            "segment_id": base_segment,
            "wavelength": 1550.12,
            "spectral_slot_width": 50.0,
            "itu_grid_position": 35,
            "chromatic_dispersion": 17.5,
            "pmd_tolerance": 2.5,
            "modulation_format": "dp_qpsk",  # Lowercase with underscore
        },
    )

    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.json()}")

    assert response.status_code == 201, f"Failed to create optical spectrum data: {response.text}"

    data = response.json()

    # Verify returned data
    assert data["segment"]["id"] == base_segment
    assert float(data["wavelength"]) == 1550.12
    assert float(data["spectral_slot_width"]) == 50.0
    assert data["itu_grid_position"] == 35
    assert float(data["chromatic_dispersion"]) == 17.5
    assert float(data["pmd_tolerance"]) == 2.5
    assert data["modulation_format"] == "dp_qpsk"

    # Verify timestamps
    assert "created" in data
    assert "last_updated" in data


def test_retrieve_optical_spectrum_data(base_segment):
    """Test retrieving optical spectrum technical data."""
    print(f"\n=== Retrieving Optical Spectrum Data for Segment {base_segment} ===")

    response = requests.get(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/optical-spectrum-data/{base_segment}/",
        headers=HEADERS,
    )

    print(f"Response status: {response.status_code}")

    assert response.status_code == 200, f"Failed to retrieve optical spectrum data: {response.text}"

    data = response.json()
    assert data["segment"]["id"] == base_segment
    assert float(data["wavelength"]) == 1550.12
    assert data["modulation_format"] == "dp_qpsk"


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
    assert float(data["type_specific_data"]["wavelength"]) == 1550.12
    assert data["type_specific_data"]["modulation_format"] == "dp_qpsk"


def test_update_optical_spectrum_data(base_segment):
    """Test updating optical spectrum technical data."""
    print(f"\n=== Updating Optical Spectrum Data for Segment {base_segment} ===")

    response = requests.patch(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/optical-spectrum-data/{base_segment}/",
        headers=HEADERS,
        json={
            "wavelength": 1552.52,  # Change wavelength
            "modulation_format": "dp_16qam",  # Change modulation (lowercase with underscore)
        },
    )

    print(f"Response status: {response.status_code}")

    assert response.status_code == 200, f"Failed to update optical spectrum data: {response.text}"

    data = response.json()
    assert float(data["wavelength"]) == 1552.52
    assert data["modulation_format"] == "dp_16qam"

    # Verify segment API reflects the update
    seg_response = requests.get(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{base_segment}/",
        headers=HEADERS,
    )
    seg_data = seg_response.json()
    assert float(seg_data["type_specific_data"]["wavelength"]) == 1552.52


def test_wavelength_validation():
    """Test wavelength range validation."""
    print("\n=== Testing Wavelength Validation ===")

    # Create a segment
    seg_response = requests.post(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/",
        headers=HEADERS,
        json={
            "name": "Wavelength Validation Test",
            "status": "active",
            "segment_type": "optical_spectrum",
            "provider": TEST_PROVIDER_ID,
            "site_a": TEST_SITE_A_ID,
            "site_b": TEST_SITE_B_ID,
        },
    )
    assert seg_response.status_code == 201
    segment_id = seg_response.json()["id"]

    try:
        # Try to create optical spectrum data with invalid wavelength (out of range)
        response = requests.post(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/optical-spectrum-data/",
            headers=HEADERS,
            json={
                "segment_id": segment_id,
                "wavelength": 2000.0,  # Out of range (max is 1625)
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


def test_delete_optical_spectrum_data(base_segment):
    """Test deleting optical spectrum technical data."""
    print(f"\n=== Deleting Optical Spectrum Data for Segment {base_segment} ===")

    response = requests.delete(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/optical-spectrum-data/{base_segment}/",
        headers=HEADERS,
    )

    print(f"Response status: {response.status_code}")

    assert response.status_code == 204, f"Failed to delete optical spectrum data: {response.text}"

    # Verify data is deleted
    get_response = requests.get(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/optical-spectrum-data/{base_segment}/",
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


def test_cascade_delete_on_segment_deletion():
    """Test that deleting a segment cascades to delete optical spectrum data."""
    print("\n=== Testing Cascade Delete ===")

    # Create segment with optical spectrum data
    seg_response = requests.post(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/",
        headers=HEADERS,
        json={
            "name": "Cascade Delete Test Segment",
            "status": "active",
            "segment_type": "optical_spectrum",
            "provider": TEST_PROVIDER_ID,
            "site_a": TEST_SITE_A_ID,
            "site_b": TEST_SITE_B_ID,
        },
    )
    assert seg_response.status_code == 201
    segment_id = seg_response.json()["id"]

    # Create optical spectrum data
    os_response = requests.post(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/optical-spectrum-data/",
        headers=HEADERS,
        json={
            "segment_id": segment_id,
            "wavelength": 1550.0,
        },
    )
    assert os_response.status_code == 201

    # Verify optical spectrum data exists
    get_os_response = requests.get(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/optical-spectrum-data/{segment_id}/",
        headers=HEADERS,
    )
    assert get_os_response.status_code == 200

    # Delete segment
    del_response = requests.delete(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{segment_id}/",
        headers=HEADERS,
    )
    assert del_response.status_code == 204

    # Verify optical spectrum data is also deleted (cascade)
    get_os_after = requests.get(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/optical-spectrum-data/{segment_id}/",
        headers=HEADERS,
    )
    assert get_os_after.status_code == 404
