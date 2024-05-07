from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer
from .segment import SegmentSerializer
from .service_path import ServicePathSerializer
from ...models import ServicePathSegmentMapping, ServicePath


class ServicePathSegmentMappingSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:komora_service_path_plugin-api:servicepathsegmentmapping-detail"
    )
    # service_path = serializers.PrimaryKeyRelatedField(
    #    queryset=ServicePath.objects.all(),
    #    required=True
    # )
    service_path = ServicePathSerializer(read_only=True)
    segment = SegmentSerializer(read_only=True)

    class Meta:
        model = ServicePathSegmentMapping
        fields = "__all__"

    def validate(self, data):
        super().validate(data)
        return data
