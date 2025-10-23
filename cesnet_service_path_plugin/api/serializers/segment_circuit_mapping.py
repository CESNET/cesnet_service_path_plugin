from circuits.api.serializers import CircuitSerializer
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers

from cesnet_service_path_plugin.api.serializers.segment import SegmentSerializer
from cesnet_service_path_plugin.models import SegmentCircuitMapping


class SegmentCircuitMappingSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:cesnet_service_path_plugin-api:segmentcircuitmapping-detail"
    )
    circuit = CircuitSerializer(nested=True)
    segment = SegmentSerializer(nested=True)

    class Meta:
        model = SegmentCircuitMapping
        fields = [
            "id",
            "url",
            "display",
            "segment",
            "circuit",
            "tags",
        ]
        brief_fields = [
            "id",
            "url",
            "display",
            "segment",
            "circuit",
        ]

    def validate(self, data):
        super().validate(data)
        return data
