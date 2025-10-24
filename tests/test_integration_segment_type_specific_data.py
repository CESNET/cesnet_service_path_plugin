"""
Integration tests for Segment type-specific data validation.
Tests cover different segment types: dark_fiber, optical_spectrum, ethernet_service.

Prerequisites:
- A running NetBox instance with the cesnet_service_path_plugin installed
- An API token with appropriate permissions set in environment variables
- Valid Provider, Site, and Location IDs in the database
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
def dark_fiber_segment_id():
    """Create a dark fiber segment with technical specifications."""
    print("\n=== Creating Dark Fiber Segment ===")

    response = requests.post(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/",
        headers=HEADERS,
        json={
            "name": "Dark Fiber Test Segment",
            "status": "active",
            "segment_type": "dark_fiber",
            "provider": TEST_PROVIDER_ID,
            "site_a": TEST_SITE_A_ID,
            "location_a": TEST_LOCATION_A_ID,
            "site_b": TEST_SITE_B_ID,
            "location_b": TEST_LOCATION_B_ID,
            "type_specific_data": {
                "fiber_type": ["G.652D", "G.655"],
                "fiber_attenuation_max": 0.25,
                "total_loss": 8.5,
                "total_length": 125.5,
                "number_of_fibers": 48,
                "connector_type_side_a": "LC/APC",
                "connector_type_side_b": "SC/APC",
            },
        },
    )
    assert response.status_code == 201, f"Failed to create: {response.text}"

    created_id = response.json()["id"]
    print(f"Created dark fiber segment with ID: {created_id}")

    yield created_id

    # Cleanup
    print(f"\n=== Deleting Dark Fiber Segment (ID: {created_id}) ===")
    requests.delete(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{created_id}/",
        headers=HEADERS,
    )


@pytest.fixture(scope="module")
def optical_spectrum_segment_id():
    """Create an optical spectrum segment with technical specifications."""
    print("\n=== Creating Optical Spectrum Segment ===")

    response = requests.post(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/",
        headers=HEADERS,
        json={
            "name": "Optical Spectrum Test Segment",
            "status": "active",
            "segment_type": "optical_spectrum",
            "provider": TEST_PROVIDER_ID,
            "site_a": TEST_SITE_A_ID,
            "location_a": TEST_LOCATION_A_ID,
            "site_b": TEST_SITE_B_ID,
            "location_b": TEST_LOCATION_B_ID,
            "type_specific_data": {
                "wavelength": 1550.12,
                "spectral_slot_width": 50.0,
                "itu_grid_position": 35,
                "chromatic_dispersion": 17.5,
                "pmd_tolerance": 2.5,
                "modulation_format": "DP-QPSK",
            },
        },
    )
    assert response.status_code == 201, f"Failed to create: {response.text}"

    created_id = response.json()["id"]
    print(f"Created optical spectrum segment with ID: {created_id}")

    yield created_id

    # Cleanup
    print(f"\n=== Deleting Optical Spectrum Segment (ID: {created_id}) ===")
    requests.delete(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{created_id}/",
        headers=HEADERS,
    )


@pytest.fixture(scope="module")
def ethernet_segment_id():
    """Create an ethernet service segment with technical specifications."""
    print("\n=== Creating Ethernet Service Segment ===")

    response = requests.post(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/",
        headers=HEADERS,
        json={
            "name": "Ethernet Service Test Segment",
            "status": "active",
            "segment_type": "ethernet_service",
            "provider": TEST_PROVIDER_ID,
            "site_a": TEST_SITE_A_ID,
            "location_a": TEST_LOCATION_A_ID,
            "site_b": TEST_SITE_B_ID,
            "location_b": TEST_LOCATION_B_ID,
            "type_specific_data": {
                "port_speed": 10000,
                "vlan_id": 100,
                "vlan_tags": "100,200,300",
                "encapsulation_type": "IEEE 802.1Q",
                "interface_type": "SFP+",
                "mtu_size": 9000,
            },
        },
    )
    assert response.status_code == 201, f"Failed to create: {response.text}"

    created_id = response.json()["id"]
    print(f"Created ethernet segment with ID: {created_id}")

    yield created_id

    # Cleanup
    print(f"\n=== Deleting Ethernet Segment (ID: {created_id}) ===")
    requests.delete(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{created_id}/",
        headers=HEADERS,
    )


def test_dark_fiber_type_specific_data(dark_fiber_segment_id):
    """Verify dark fiber technical data is stored correctly."""
    print(f"\n=== Verifying Dark Fiber Data (ID: {dark_fiber_segment_id}) ===")

    response = requests.get(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{dark_fiber_segment_id}/",
        headers=HEADERS,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["segment_type"] == "dark_fiber"
    assert data["type_specific_data"]["fiber_type"] == ["G.652D", "G.655"]
    assert float(data["type_specific_data"]["fiber_attenuation_max"]) == 0.25
    assert float(data["type_specific_data"]["total_loss"]) == 8.5
    assert float(data["type_specific_data"]["total_length"]) == 125.5
    assert data["type_specific_data"]["number_of_fibers"] == 48
    assert data["type_specific_data"]["connector_type_side_a"] == "LC/APC"


def test_update_dark_fiber_technical_data(dark_fiber_segment_id):
    """Test updating dark fiber technical specifications."""
    print(f"\n=== Updating Dark Fiber Technical Data (ID: {dark_fiber_segment_id}) ===")

    response = requests.patch(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{dark_fiber_segment_id}/",
        headers=HEADERS,
        json={
            "type_specific_data": {
                "fiber_type": ["G.652D"],
                "total_loss": 7.2,
                "number_of_fibers": 96,
            }
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert data["type_specific_data"]["fiber_type"] == ["G.652D"]
    assert float(data["type_specific_data"]["total_loss"]) == 7.2
    assert data["type_specific_data"]["number_of_fibers"] == 96


def test_optical_spectrum_type_specific_data(optical_spectrum_segment_id):
    """Verify optical spectrum technical data is stored correctly."""
    print(f"\n=== Verifying Optical Spectrum Data (ID: {optical_spectrum_segment_id}) ===")

    response = requests.get(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{optical_spectrum_segment_id}/",
        headers=HEADERS,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["segment_type"] == "optical_spectrum"
    assert float(data["type_specific_data"]["wavelength"]) == 1550.12
    assert float(data["type_specific_data"]["spectral_slot_width"]) == 50.0
    assert data["type_specific_data"]["itu_grid_position"] == 35
    assert data["type_specific_data"]["modulation_format"] == "DP-QPSK"


def test_ethernet_service_type_specific_data(ethernet_segment_id):
    """Verify ethernet service technical data is stored correctly."""
    print(f"\n=== Verifying Ethernet Service Data (ID: {ethernet_segment_id}) ===")

    response = requests.get(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{ethernet_segment_id}/",
        headers=HEADERS,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["segment_type"] == "ethernet_service"
    assert data["type_specific_data"]["port_speed"] == 10000
    assert data["type_specific_data"]["vlan_id"] == 100
    assert data["type_specific_data"]["encapsulation_type"] == "IEEE 802.1Q"
    assert data["type_specific_data"]["interface_type"] == "SFP+"
    assert data["type_specific_data"]["mtu_size"] == 9000


def test_change_segment_type(dark_fiber_segment_id):
    """Test changing segment type and updating technical data."""
    print(f"\n=== Changing Segment Type (ID: {dark_fiber_segment_id}) ===")

    # Change from dark_fiber to ethernet_service
    response = requests.patch(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{dark_fiber_segment_id}/",
        headers=HEADERS,
        json={
            "segment_type": "ethernet_service",
            "type_specific_data": {
                "port_speed": 1000,
                "vlan_id": 50,
                "interface_type": "RJ45",
            },
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert data["segment_type"] == "ethernet_service"
    assert data["type_specific_data"]["port_speed"] == 1000
    assert data["type_specific_data"]["vlan_id"] == 50
