from ipam.api.nested_serializers import NestedIPAddressSerializer, NestedPrefixSerializer, NestedVRFSerializer
from dcim.api.nested_serializers import NestedDeviceSerializer
from netbox.api.serializers import NetBoxModelSerializer, WritableNestedSerializer
from rest_framework import serializers

from ...models.segment import Segment


class SegmentSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:komora_service_path_plugin-api:segment-detail")

    class Meta:
        model = Segment
        fields = (
            "id",
            "url",)

    # def validate(self, data):
    #    # Enforce model validation
    #    super().validate(data)
    #    return data
