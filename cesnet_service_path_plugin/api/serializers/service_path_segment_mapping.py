from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer
from komora_service_path_plugin.api.serializers.segment import SegmentSerializer
from komora_service_path_plugin.api.serializers.service_path import ServicePathSerializer
from komora_service_path_plugin.models import ServicePathSegmentMapping


class ServicePathSegmentMappingSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:komora_service_path_plugin-api:servicepathsegmentmapping-detail"
    )
    # service_path = serializers.PrimaryKeyRelatedField(
    #    queryset=ServicePath.objects.all(),
    #    required=True
    # )
    service_path = ServicePathSerializer(nested=True)
    segment = SegmentSerializer(nested=True)

    class Meta:
        model = ServicePathSegmentMapping
        fields = [
            "id",
            "url",
            "display",
            "service_path",
            "segment",
            "komora_id",
            "index",
        ]
        brief_fields = [
            "id",
            "url",
            "display",
            "service_path",
            "segment",
            "komora_id",
            "index",
        ]

    def validate(self, data):
        super().validate(data)
        return data
