from netbox.api.viewsets import NetBoxModelViewSet

from cesnet_service_path_plugin.models import EthernetServiceSegmentData
from cesnet_service_path_plugin.api.serializers.ethernet_service_data_serializer import (
    EthernetServiceSegmentDataSerializer,
)


class EthernetServiceSegmentDataViewSet(NetBoxModelViewSet):
    """
    API viewset for managing Ethernet Service technical data.

    Provides CRUD operations for ethernet service segment technical specifications.
    """

    queryset = EthernetServiceSegmentData.objects.select_related('segment').all()
    serializer_class = EthernetServiceSegmentDataSerializer
