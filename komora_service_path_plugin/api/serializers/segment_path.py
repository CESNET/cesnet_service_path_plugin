from ipam.api.nested_serializers import NestedIPAddressSerializer, NestedPrefixSerializer, NestedVRFSerializer
from dcim.api.nested_serializers import NestedDeviceSerializer
from netbox.api.serializers import NetBoxModelSerializer, WritableNestedSerializer
from rest_framework import serializers

from ...models.segment_path import SegmentPath


class SegmentPathSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:komora_service_path_plugin-api:segmentpath-detail")

    class Meta:
        model = SegmentPath
        fields = (
            "id",
            "url",)

    # def validate(self, data):
    #    # Enforce model validation
    #    super().validate(data)
    #    return data
