from netbox.api.viewsets import NetBoxModelViewSet

from cesnet_service_path_plugin.models import DarkFiberSegmentData
from cesnet_service_path_plugin.api.serializers.dark_fiber_data_serializer import (
    DarkFiberSegmentDataSerializer,
)


class DarkFiberSegmentDataViewSet(NetBoxModelViewSet):
    """
    API viewset for managing Dark Fiber technical data.

    Provides CRUD operations for dark fiber segment technical specifications.
    """

    queryset = DarkFiberSegmentData.objects.select_related('segment').all()
    serializer_class = DarkFiberSegmentDataSerializer
