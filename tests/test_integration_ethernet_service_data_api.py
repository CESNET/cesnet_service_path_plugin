"""
Integration tests for Ethernet Service Data API endpoints.

Tests the new type-specific data model API for ethernet service segments.

Prerequisites:
- A running NetBox instance with the cesnet_service_path_plugin installed
- An API token with appropriate permissions set in environment variables
- Valid Provider, Site, and Location IDs in the database

Run with:
    /home/albert/cesnet/netbox/venv/bin/python -m pytest tests/test_integration_ethernet_service_data_api.py -v
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
    """Create an ethernet service segment WITHOUT technical data."""
    print("\n=== Creating Base Ethernet Service Segment (No Technical Data) ===")

    response = requests.post(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/",
        headers=HEADERS,
        json={
            "name": "Test Ethernet Service Segment for API",
            "status": "active",
            "segment_type": "ethernet_service",
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


def test_create_ethernet_service_data(base_segment):
    """Test creating ethernet service technical data for a segment."""
    print(f"\n=== Creating Ethernet Service Technical Data for Segment {base_segment} ===")

    response = requests.post(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/ethernet-service-data/",
        headers=HEADERS,
        json={
            "segment_id": base_segment,
            "port_speed": 10000,
            "vlan_id": 100,
            "vlan_tags": "100,200,300",
            "encapsulation_type": "dot1q",  # Lowercase
            "interface_type": "sfp_plus",  # Lowercase with underscore
            "mtu_size": 9000,
        },
    )

    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.json()}")

    assert response.status_code == 201, f"Failed to create ethernet service data: {response.text}"

    data = response.json()

    # Verify returned data
    assert data["segment"]["id"] == base_segment
    assert data["port_speed"] == 10000
    assert data["vlan_id"] == 100
    assert data["vlan_tags"] == "100,200,300"
    assert data["encapsulation_type"] == "dot1q"
    assert data["interface_type"] == "sfp_plus"
    assert data["mtu_size"] == 9000

    # Verify timestamps
    assert "created" in data
    assert "last_updated" in data


def test_retrieve_ethernet_service_data(base_segment):
    """Test retrieving ethernet service technical data."""
    print(f"\n=== Retrieving Ethernet Service Data for Segment {base_segment} ===")

    response = requests.get(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/ethernet-service-data/{base_segment}/",
        headers=HEADERS,
    )

    print(f"Response status: {response.status_code}")

    assert response.status_code == 200, f"Failed to retrieve ethernet service data: {response.text}"

    data = response.json()
    assert data["segment"]["id"] == base_segment
    assert data["port_speed"] == 10000
    assert data["vlan_id"] == 100
    assert data["interface_type"] == "sfp_plus"


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
    assert data["type_specific_data"]["port_speed"] == 10000
    assert data["type_specific_data"]["vlan_id"] == 100
    assert data["type_specific_data"]["interface_type"] == "sfp_plus"


def test_update_ethernet_service_data(base_segment):
    """Test updating ethernet service technical data."""
    print(f"\n=== Updating Ethernet Service Data for Segment {base_segment} ===")

    response = requests.patch(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/ethernet-service-data/{base_segment}/",
        headers=HEADERS,
        json={
            "port_speed": 100000,  # Upgrade to 100G
            "interface_type": "qsfp28",  # Lowercase
            "mtu_size": 9216,  # Jumbo frames
        },
    )

    print(f"Response status: {response.status_code}")

    assert response.status_code == 200, f"Failed to update ethernet service data: {response.text}"

    data = response.json()
    assert data["port_speed"] == 100000
    assert data["interface_type"] == "qsfp28"
    assert data["mtu_size"] == 9216

    # Verify segment API reflects the update
    seg_response = requests.get(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{base_segment}/",
        headers=HEADERS,
    )
    seg_data = seg_response.json()
    assert seg_data["type_specific_data"]["port_speed"] == 100000


def test_vlan_id_validation():
    """Test VLAN ID validation (0 and 4095 are reserved)."""
    print("\n=== Testing VLAN ID Validation ===")

    # Create a segment
    seg_response = requests.post(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/",
        headers=HEADERS,
        json={
            "name": "VLAN Validation Test",
            "status": "active",
            "segment_type": "ethernet_service",
            "provider": TEST_PROVIDER_ID,
            "site_a": TEST_SITE_A_ID,
            "site_b": TEST_SITE_B_ID,
        },
    )
    assert seg_response.status_code == 201
    segment_id = seg_response.json()["id"]

    try:
        # Try to create ethernet service data with reserved VLAN ID 0
        response1 = requests.post(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/ethernet-service-data/",
            headers=HEADERS,
            json={
                "segment_id": segment_id,
                "vlan_id": 0,  # Reserved
            },
        )

        print(f"VLAN 0 validation response: {response1.status_code}")
        print(f"VLAN 0 validation response body: {response1.json()}")

        # Should fail validation (400 Bad Request)
        assert response1.status_code == 400

        # Try with VLAN ID 4095 (also reserved)
        response2 = requests.post(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/ethernet-service-data/",
            headers=HEADERS,
            json={
                "segment_id": segment_id,
                "vlan_id": 4095,  # Reserved
            },
        )

        print(f"VLAN 4095 validation response: {response2.status_code}")

        # Should fail validation (400 Bad Request)
        assert response2.status_code == 400

    finally:
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{segment_id}/",
            headers=HEADERS,
        )


def test_vlan_tags_format_validation():
    """Test VLAN tags format validation."""
    print("\n=== Testing VLAN Tags Format Validation ===")

    # Create a segment
    seg_response = requests.post(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/",
        headers=HEADERS,
        json={
            "name": "VLAN Tags Validation Test",
            "status": "active",
            "segment_type": "ethernet_service",
            "provider": TEST_PROVIDER_ID,
            "site_a": TEST_SITE_A_ID,
            "site_b": TEST_SITE_B_ID,
        },
    )
    assert seg_response.status_code == 201
    segment_id = seg_response.json()["id"]

    try:
        # Try to create ethernet service data with invalid VLAN tags (non-numeric)
        response = requests.post(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/ethernet-service-data/",
            headers=HEADERS,
            json={
                "segment_id": segment_id,
                "vlan_tags": "100,abc,300",  # Invalid: 'abc' is not numeric
            },
        )

        print(f"VLAN tags validation response: {response.status_code}")
        print(f"VLAN tags validation response body: {response.json()}")

        # Should fail validation (400 Bad Request)
        assert response.status_code == 400

    finally:
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{segment_id}/",
            headers=HEADERS,
        )


def test_mtu_size_validation():
    """Test MTU size validation."""
    print("\n=== Testing MTU Size Validation ===")

    # Create a segment
    seg_response = requests.post(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/",
        headers=HEADERS,
        json={
            "name": "MTU Validation Test",
            "status": "active",
            "segment_type": "ethernet_service",
            "provider": TEST_PROVIDER_ID,
            "site_a": TEST_SITE_A_ID,
            "site_b": TEST_SITE_B_ID,
        },
    )
    assert seg_response.status_code == 201
    segment_id = seg_response.json()["id"]

    try:
        # Try to create ethernet service data with MTU below minimum for IP (576)
        response = requests.post(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/ethernet-service-data/",
            headers=HEADERS,
            json={
                "segment_id": segment_id,
                "mtu_size": 500,  # Below minimum of 576
            },
        )

        print(f"MTU validation response: {response.status_code}")
        print(f"MTU validation response body: {response.json()}")

        # Should fail validation (400 Bad Request)
        assert response.status_code == 400

    finally:
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{segment_id}/",
            headers=HEADERS,
        )


def test_delete_ethernet_service_data(base_segment):
    """Test deleting ethernet service technical data."""
    print(f"\n=== Deleting Ethernet Service Data for Segment {base_segment} ===")

    response = requests.delete(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/ethernet-service-data/{base_segment}/",
        headers=HEADERS,
    )

    print(f"Response status: {response.status_code}")

    assert response.status_code == 204, f"Failed to delete ethernet service data: {response.text}"

    # Verify data is deleted
    get_response = requests.get(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/ethernet-service-data/{base_segment}/",
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
    """Test that deleting a segment cascades to delete ethernet service data."""
    print("\n=== Testing Cascade Delete ===")

    # Create segment with ethernet service data
    seg_response = requests.post(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/",
        headers=HEADERS,
        json={
            "name": "Cascade Delete Test Segment",
            "status": "active",
            "segment_type": "ethernet_service",
            "provider": TEST_PROVIDER_ID,
            "site_a": TEST_SITE_A_ID,
            "site_b": TEST_SITE_B_ID,
        },
    )
    assert seg_response.status_code == 201
    segment_id = seg_response.json()["id"]

    # Create ethernet service data
    es_response = requests.post(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/ethernet-service-data/",
        headers=HEADERS,
        json={
            "segment_id": segment_id,
            "port_speed": 10000,
            "vlan_id": 100,
        },
    )
    assert es_response.status_code == 201

    # Verify ethernet service data exists
    get_es_response = requests.get(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/ethernet-service-data/{segment_id}/",
        headers=HEADERS,
    )
    assert get_es_response.status_code == 200

    # Delete segment
    del_response = requests.delete(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{segment_id}/",
        headers=HEADERS,
    )
    assert del_response.status_code == 204

    # Verify ethernet service data is also deleted (cascade)
    get_es_after = requests.get(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/ethernet-service-data/{segment_id}/",
        headers=HEADERS,
    )
    assert get_es_after.status_code == 404
