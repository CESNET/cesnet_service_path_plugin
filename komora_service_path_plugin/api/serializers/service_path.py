from ipam.api.nested_serializers import NestedIPAddressSerializer, NestedPrefixSerializer, NestedVRFSerializer
from dcim.api.nested_serializers import NestedDeviceSerializer
from netbox.api.serializers import NetBoxModelSerializer, WritableNestedSerializer
from rest_framework import serializers

from ...models.service_path import ServicePath


class ServicePathSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:komora_service_path_plugin-api:servicepath-detail")

    class Meta:
        model = ServicePath
        fields = (
            "id",
            "url",)

    # def validate(self, data):
    #    # Enforce model validation
    #    super().validate(data)
    #    return data
