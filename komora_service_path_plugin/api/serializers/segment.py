from rest_framework import serializers
from tenancy.api.nested_serializers import NestedTenantSerializer
from dcim.api.nested_serializers import NestedSiteSerializer, NestedLocationSerializer, NestedDeviceSerializer, NestedInterfaceSerializer
from netbox.api.serializers import NetBoxModelSerializer, WritableNestedSerializer

from ...models.segment import Segment

class SegmentSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:komora_service_path_plugin-api:segment-detail"
    )
    supplier = NestedTenantSerializer(read_only=True)
    site_a = NestedSiteSerializer(read_only=True)
    location_a = NestedLocationSerializer(read_only=True)
    device_a = NestedDeviceSerializer(read_only=True)
    port_a = NestedInterfaceSerializer(read_only=True)
    site_b = NestedSiteSerializer(read_only=True)
    location_b = NestedLocationSerializer(read_only=True)
    device_b = NestedDeviceSerializer(read_only=True)
    port_b = NestedInterfaceSerializer(read_only=True)

    class Meta:
        model = Segment
        fields = (
            "id",
            "url",
            "name",
            "network_label",
            "install_date",
            "termination_date",
            "supplier",
            "supplier_segment_id",
            "supplier_segment_name",
            "supplier_segment_contract",
            "site_a",
            "location_a",
            "device_a",
            "port_a",
            "note_a",
            "site_b",
            "location_b",
            "device_b",
            "port_b",
            "note_b",
            "imported_data",
        )

    def validate(self, data):
        # Enforce model validation
        super().validate(data)
        return data