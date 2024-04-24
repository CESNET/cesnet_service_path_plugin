from netbox.api.metadata import ContentTypeMetadata
from netbox.api.viewsets import NetBoxModelViewSet

from ... import filtersets, models
from ..serializers import SegmentSerializer


class SegmentViewSet(NetBoxModelViewSet):
    metadata_class = ContentTypeMetadata
    queryset = models.Segment.objects.all()
    serializer_class = SegmentSerializer
    filterset_class = filtersets.SegmentFilterSet
