from netbox.api.metadata import ContentTypeMetadata
from netbox.api.viewsets import NetBoxModelViewSet

from cesnet_service_path_plugin import filtersets, models
from cesnet_service_path_plugin.api.serializers import SegmentCircuitMappingSerializer


class SegmnetCircuitMappingViewSet(NetBoxModelViewSet):
    metadata_class = ContentTypeMetadata
    queryset = models.SegmentCircuitMapping.objects.all()
    serializer_class = SegmentCircuitMappingSerializer
    filterset_class = filtersets.SegmentCircuitMappingFilterSet
