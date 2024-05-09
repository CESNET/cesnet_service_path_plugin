from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer
from .segment import WritableNestedSegmentSerializer
from .service_path import WritableNestedServicePathSerializer
from ...models import ServicePathSegmentMapping


class ServicePathSegmentMappingSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:komora_service_path_plugin-api:servicepathsegmentmapping-detail"
    )
    # service_path = serializers.PrimaryKeyRelatedField(
    #    queryset=ServicePath.objects.all(),
    #    required=True
    # )
    service_path = WritableNestedServicePathSerializer()
    segment = WritableNestedSegmentSerializer()

    class Meta:
        model = ServicePathSegmentMapping
        fields = "__all__"

    def validate(self, data):
        super().validate(data)
        return data
