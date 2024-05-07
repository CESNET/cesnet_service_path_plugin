from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer
from .segment import SegmentSerializer
from ...models import ServicePath


class ServicePathSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:komora_service_path_plugin-api:servicepath-detail"
    )
    # segments = SegmentSerializer(many=True, read_only=True)

    class Meta:
        model = ServicePath
        fields = "__all__"

    def validate(self, data):
        super().validate(data)
        return data
