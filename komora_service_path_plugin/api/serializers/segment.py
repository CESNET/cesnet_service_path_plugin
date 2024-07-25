from circuits.api.serializers import CircuitSerializer, ProviderSerializer
from dcim.api.serializers import (
    DeviceSerializer,
    InterfaceSerializer,
    LocationSerializer,
    SiteSerializer,
)
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers

from komora_service_path_plugin.models.segment import Segment


class SegmentSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:komora_service_path_plugin-api:segment-detail"
    )
    provider = ProviderSerializer(required=True, nested=True)
    site_a = SiteSerializer(required=True, nested=True)
    location_a = LocationSerializer(required=True, nested=True)
    device_a = DeviceSerializer(required=False, allow_null=True, nested=True)
    port_a = InterfaceSerializer(required=False, allow_null=True, nested=True)
    site_b = SiteSerializer(required=True, nested=True)
    location_b = LocationSerializer(required=True, nested=True)
    device_b = DeviceSerializer(required=False, allow_null=True, nested=True)
    port_b = InterfaceSerializer(required=False, allow_null=True, nested=True)
    circuits = CircuitSerializer(required=False, many=True, nested=True)

    class Meta:
        model = Segment
        fields = (
            "id",
            "url",
            "display",
            "name",
            "network_label",
            "install_date",
            "termination_date",
            "provider",
            "provider_segment_id",
            "provider_segment_name",
            "provider_segment_contract",
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
            "komora_id",
            "circuits",
        )
        brief_fields = (
            "id",
            "url",
            "display",
            "name",
            "komora_id",
        )

    def validate(self, data):
        # Enforce model validation
        super().validate(data)
        return data
