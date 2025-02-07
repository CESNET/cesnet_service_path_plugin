from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer
from komora_service_path_plugin.api.serializers.segment import SegmentSerializer
from komora_service_path_plugin.api.serializers.service_path import ServicePathSerializer
from komora_service_path_plugin.models import SegmentCircuitMapping
from circuits.api.serializers import CircuitSerializer

class SegmentCircuitMappingSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:komora_service_path_plugin-api:segmentcircuitmapping-detail"
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
