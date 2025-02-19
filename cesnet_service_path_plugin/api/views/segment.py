from netbox.api.metadata import ContentTypeMetadata
from netbox.api.viewsets import NetBoxModelViewSet

from cesnet_service_path_plugin.models import Segment
from cesnet_service_path_plugin.filtersets import SegmentFilterSet
from cesnet_service_path_plugin.api.serializers import SegmentSerializer


class SegmentViewSet(NetBoxModelViewSet):
    metadata_class = ContentTypeMetadata
    queryset = Segment.objects.all()
    serializer_class = SegmentSerializer
    filterset_class = SegmentFilterSet
