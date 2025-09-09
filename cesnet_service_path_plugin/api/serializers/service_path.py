from circuits.api.serializers import CircuitSerializer
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers

from cesnet_service_path_plugin.api.serializers.segment import SegmentSerializer
from cesnet_service_path_plugin.models import ServicePath


class ServicePathSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:cesnet_service_path_plugin-api:servicepath-detail"
    )
    segments = SegmentSerializer(many=True, read_only=True, nested=True)
    circuits = CircuitSerializer(required=False, many=True, nested=True)

    class Meta:
        model = ServicePath
        fields = [
            "id",
            "url",
            "display",
            "name",
            "status",
            "kind",
            "segments",
            "circuits",
            "tags",
        ]
        brief_fields = [
            "id",
            "url",
            "display",
            "name",
            "tags",
        ]

    def validate(self, data):
        super().validate(data)
        return data
