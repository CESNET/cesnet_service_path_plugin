from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer
from komora_service_path_plugin.api.serializers.segment import SegmentSerializer
from komora_service_path_plugin.models import ServicePath


class ServicePathSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:komora_service_path_plugin-api:servicepath-detail"
    )
    segments = SegmentSerializer(many=True, read_only=True, nested=True)

    class Meta:
        model = ServicePath
        fields = [
            "id",
            "url",
            "display",
            "name",
            "state",
            "kind",
            "segments",
            "komora_id",
        ]
        brief_fields = [
            "id",
            "url",
            "name",
            "komora_id",
        ]

    def validate(self, data):
        super().validate(data)
        return data
