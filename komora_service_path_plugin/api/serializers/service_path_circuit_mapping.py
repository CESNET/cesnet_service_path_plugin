from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer
from komora_service_path_plugin.api.serializers.segment import SegmentSerializer
from komora_service_path_plugin.api.serializers.service_path import ServicePathSerializer
from komora_service_path_plugin.models import ServicePathCircuitMapping
from circuits.api.serializers import CircuitSerializer


class ServicePathCircuitMappingSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:komora_service_path_plugin-api:servicepathcircuitmapping-detail"
    )
    circuit = CircuitSerializer(nested=True)
    service_path = ServicePathSerializer(nested=True)

    class Meta:
        model = ServicePathCircuitMapping
        fields = [
            "id",
            "url",
            "display",
            "service_path",
            "circuit",
        ]
        brief_fields = [
            "id",
            "url",
            "display",
            "service_path",
            "circuit",
        ]

    def validate(self, data):
        super().validate(data)
        return data
