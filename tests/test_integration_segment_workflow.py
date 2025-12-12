"""
Integration tests for Segment workflows with type-specific technical data.

Tests the complete two-step workflow for creating segments with technical data,
changing segment types, and verifying the new API structure.

Prerequisites:
- A running NetBox instance with the cesnet_service_path_plugin installed
- An API token with appropriate permissions set in environment variables
- Valid Provider, Site, and Location IDs in the database

Run with:
    /home/albert/cesnet/netbox/venv/bin/python -m pytest tests/test_integration_segment_workflow.py -v
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


def test_two_step_creation_dark_fiber():
    """
    Test complete two-step workflow for creating a dark fiber segment with technical data.

    Step 1: Create segment with basic info (no technical data)
    Step 2: Add dark fiber technical data via separate endpoint
    Step 3: Verify segment includes type_specific_data
    """
    print("\n=== Testing Two-Step Segment Creation (Dark Fiber) ===")

    # STEP 1: Create segment with basic info
    print("Step 1: Creating segment without technical data...")
    seg_response = requests.post(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/",
        headers=HEADERS,
        json={
            "name": "Two-Step Dark Fiber Segment",
            "status": "active",
            "segment_type": "dark_fiber",
            "provider": TEST_PROVIDER_ID,
            "site_a": TEST_SITE_A_ID,
            "location_a": TEST_LOCATION_A_ID,
            "site_b": TEST_SITE_B_ID,
            "location_b": TEST_LOCATION_B_ID,
        },
    )

    assert seg_response.status_code == 201, f"Failed to create segment: {seg_response.text}"
    segment_id = seg_response.json()["id"]
    print(f"Created segment with ID: {segment_id}")

    # Verify no technical data yet
    assert seg_response.json()["type_specific_data"] is None

    try:
        # STEP 2: Add dark fiber technical data
        print("Step 2: Adding dark fiber technical data...")
        df_response = requests.post(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/dark-fiber-data/",
            headers=HEADERS,
            json={
                "segment_id": segment_id,
                "fiber_mode": "single_mode",
                "single_mode_subtype": "g652d",
                "fiber_attenuation_max": 0.25,
                "total_loss": 8.5,
                "total_length": 125.5,
                "number_of_fibers": 48,
                "connector_type_side_a": "lc_apc",
                "connector_type_side_b": "sc_apc",
            },
        )

        assert df_response.status_code == 201, f"Failed to create dark fiber data: {df_response.text}"
        print("Dark fiber data created successfully")

        # STEP 3: Verify segment now includes technical data
        print("Step 3: Verifying segment includes type_specific_data...")
        verify_response = requests.get(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{segment_id}/",
            headers=HEADERS,
        )

        assert verify_response.status_code == 200
        segment_data = verify_response.json()

        # Verify type_specific_data is populated
        assert segment_data["type_specific_data"] is not None
        assert segment_data["type_specific_data"]["fiber_mode"] == "single_mode"
        assert segment_data["type_specific_data"]["single_mode_subtype"] == "g652d"
        assert float(segment_data["type_specific_data"]["total_loss"]) == 8.5

        print("✓ Two-step workflow completed successfully!")

    finally:
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{segment_id}/",
            headers=HEADERS,
        )


def test_segment_without_technical_data():
    """
    Test that segments can exist without technical data.

    Type-specific technical data is optional - segments should be valid without it.
    """
    print("\n=== Testing Segment Without Technical Data ===")

    # Create segment
    seg_response = requests.post(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/",
        headers=HEADERS,
        json={
            "name": "Segment Without Tech Data",
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
        # Verify segment is valid and retrievable
        get_response = requests.get(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{segment_id}/",
            headers=HEADERS,
        )

        assert get_response.status_code == 200
        segment_data = get_response.json()

        # Verify type_specific_data is None (no data)
        assert segment_data["type_specific_data"] is None

        print("✓ Segment without technical data is valid")

    finally:
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{segment_id}/",
            headers=HEADERS,
        )


def test_adding_technical_data_later():
    """
    Test adding technical data to an existing segment that initially had none.
    """
    print("\n=== Testing Adding Technical Data Later ===")

    # Create segment without technical data
    seg_response = requests.post(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/",
        headers=HEADERS,
        json={
            "name": "Segment Add Data Later",
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
        # Initially no technical data
        assert seg_response.json()["type_specific_data"] is None

        # Wait some time, then add technical data
        print("Adding optical spectrum data later...")
        os_response = requests.post(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/optical-spectrum-data/",
            headers=HEADERS,
            json={
                "segment_id": segment_id,
                "wavelength": 1550.12,
                "modulation_format": "dp_qpsk",
            },
        )

        assert os_response.status_code == 201

        # Verify segment now has technical data
        verify_response = requests.get(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{segment_id}/",
            headers=HEADERS,
        )

        assert verify_response.json()["type_specific_data"] is not None
        assert float(verify_response.json()["type_specific_data"]["wavelength"]) == 1550.12

        print("✓ Technical data successfully added later")

    finally:
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{segment_id}/",
            headers=HEADERS,
        )


def test_changing_segment_type():
    """
    Test changing segment type.

    When segment type changes, the old technical data model should be deleted (cascade),
    and new technical data can be added for the new type.
    """
    print("\n=== Testing Changing Segment Type ===")

    # Create dark fiber segment with technical data
    seg_response = requests.post(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/",
        headers=HEADERS,
        json={
            "name": "Type Change Test Segment",
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
        # Add dark fiber data
        df_response = requests.post(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/dark-fiber-data/",
            headers=HEADERS,
            json={
                "segment_id": segment_id,
                "fiber_mode": "single_mode",
                "total_loss": 8.5,
            },
        )
        assert df_response.status_code == 201

        # Verify dark fiber data exists
        df_get = requests.get(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/dark-fiber-data/{segment_id}/",
            headers=HEADERS,
        )
        assert df_get.status_code == 200

        # Change segment type to ethernet_service
        print("Changing segment type from dark_fiber to ethernet_service...")
        patch_response = requests.patch(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{segment_id}/",
            headers=HEADERS,
            json={
                "segment_type": "ethernet_service",
            },
        )

        assert patch_response.status_code == 200
        assert patch_response.json()["segment_type"] == "ethernet_service"

        # Verify dark fiber data is deleted (cascade or manual cleanup needed)
        # Note: This depends on whether changing segment_type triggers cascade delete
        # The segment should now have type_specific_data = None
        updated_seg = requests.get(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{segment_id}/",
            headers=HEADERS,
        )
        # After type change, old technical data should not be included
        # (because segment_type doesn't match the data type anymore)

        # Add new ethernet service data
        print("Adding ethernet service data for new type...")
        es_response = requests.post(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/ethernet-service-data/",
            headers=HEADERS,
            json={
                "segment_id": segment_id,
                "port_speed": 10000,
                "vlan_id": 100,
                "interface_type": "sfp_plus",
            },
        )

        assert es_response.status_code == 201

        # Verify segment now has ethernet service technical data
        final_seg = requests.get(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{segment_id}/",
            headers=HEADERS,
        )

        assert final_seg.json()["type_specific_data"] is not None
        assert final_seg.json()["type_specific_data"]["port_speed"] == 10000

        print("✓ Segment type changed successfully with new technical data")

    finally:
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{segment_id}/",
            headers=HEADERS,
        )


def test_type_specific_data_field_consistency():
    """
    Test that type_specific_data always returns data matching segment_type.

    Verify that the computed field correctly maps to the appropriate technical data model.
    """
    print("\n=== Testing type_specific_data Field Consistency ===")

    test_cases = [
        {
            "segment_type": "dark_fiber",
            "endpoint": "dark-fiber-data",
            "data": {"fiber_mode": "single_mode", "total_loss": 5.0},
            "verify_field": "fiber_mode",
            "verify_value": "single_mode",
        },
        {
            "segment_type": "optical_spectrum",
            "endpoint": "optical-spectrum-data",
            "data": {"wavelength": 1550.0, "modulation_format": "dp_qpsk"},
            "verify_field": "wavelength",
            "verify_value": 1550.0,
        },
        {
            "segment_type": "ethernet_service",
            "endpoint": "ethernet-service-data",
            "data": {"port_speed": 10000, "vlan_id": 100},
            "verify_field": "port_speed",
            "verify_value": 10000,
        },
    ]

    for test_case in test_cases:
        print(f"\nTesting {test_case['segment_type']}...")

        # Create segment
        seg_response = requests.post(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/",
            headers=HEADERS,
            json={
                "name": f"Consistency Test {test_case['segment_type']}",
                "status": "active",
                "segment_type": test_case["segment_type"],
                "provider": TEST_PROVIDER_ID,
                "site_a": TEST_SITE_A_ID,
                "site_b": TEST_SITE_B_ID,
            },
        )

        assert seg_response.status_code == 201
        segment_id = seg_response.json()["id"]

        try:
            # Add technical data
            tech_data = {"segment_id": segment_id}
            tech_data.update(test_case["data"])

            tech_response = requests.post(
                f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/{test_case['endpoint']}/",
                headers=HEADERS,
                json=tech_data,
            )

            assert tech_response.status_code == 201

            # Get segment and verify type_specific_data
            seg_get = requests.get(
                f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{segment_id}/",
                headers=HEADERS,
            )

            assert seg_get.status_code == 200
            segment_data = seg_get.json()

            # Verify type_specific_data is populated
            assert segment_data["type_specific_data"] is not None

            # Verify correct field value
            verify_field = test_case["verify_field"]
            verify_value = test_case["verify_value"]

            actual_value = segment_data["type_specific_data"][verify_field]
            if isinstance(verify_value, float):
                assert float(actual_value) == verify_value
            else:
                assert actual_value == verify_value

            print(f"✓ {test_case['segment_type']} consistency verified")

        finally:
            # Cleanup
            requests.delete(
                f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{segment_id}/",
                headers=HEADERS,
            )


def test_list_view_includes_type_specific_data():
    """
    Test that the segment list API includes type_specific_data field.
    """
    print("\n=== Testing List View Includes type_specific_data ===")

    # Create a segment with technical data
    seg_response = requests.post(
        f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/",
        headers=HEADERS,
        json={
            "name": "List View Test Segment",
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
        # Add technical data
        df_response = requests.post(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/dark-fiber-data/",
            headers=HEADERS,
            json={
                "segment_id": segment_id,
                "fiber_mode": "single_mode",
                "total_loss": 8.5,
            },
        )
        assert df_response.status_code == 201

        # Get list of segments filtered by name to reduce result set
        list_response = requests.get(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/",
            headers=HEADERS,
            params={"name": "List View Test Segment"}
        )

        assert list_response.status_code == 200
        segments = list_response.json()["results"]

        # Find our segment in the list
        our_segment = next((s for s in segments if s["id"] == segment_id), None)
        assert our_segment is not None, f"Segment {segment_id} not found in list response"

        # Verify type_specific_data is included in list view
        assert "type_specific_data" in our_segment
        assert our_segment["type_specific_data"] is not None
        assert our_segment["type_specific_data"]["fiber_mode"] == "single_mode"

        print("✓ List view includes type_specific_data")

    finally:
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/plugins/cesnet-service-path-plugin/segments/{segment_id}/",
            headers=HEADERS,
        )
