from netbox.api.metadata import ContentTypeMetadata
from netbox.api.viewsets import NetBoxModelViewSet

from ... import filtersets, models
from ..serializers import SegmentPathSerializer


class SegmentPathViewSet(NetBoxModelViewSet):
    metadata_class = ContentTypeMetadata
    queryset = models.SegmentPath.objects.all()
    serializer_class = SegmentPathSerializer
    filterset_class = filtersets.SegmentPathFilterSet
