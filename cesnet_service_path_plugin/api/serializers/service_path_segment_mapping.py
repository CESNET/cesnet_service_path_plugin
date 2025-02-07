from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer
from cesnet_service_path_plugin.api.serializers.segment import SegmentSerializer
from cesnet_service_path_plugin.api.serializers.service_path import (
    ServicePathSerializer,
)
from cesnet_service_path_plugin.models import ServicePathSegmentMapping


class ServicePathSegmentMappingSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:cesnet_service_path_plugin-api:servicepathsegmentmapping-detail"
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
        ]
        brief_fields = [
            "id",
            "url",
            "display",
            "service_path",
            "segment",
        ]

    def validate(self, data):
        super().validate(data)
        return data
