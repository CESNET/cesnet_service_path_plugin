from netbox.api.metadata import ContentTypeMetadata
from netbox.api.viewsets import NetBoxModelViewSet

from ... import filtersets, models
from ..serializers import ServicePathSegmentMappingSerializer


class ServicePathSegmentMappingViewSet(NetBoxModelViewSet):
    metadata_class = ContentTypeMetadata
    queryset = models.ServicePathSegmentMapping.objects.all()
    serializer_class = ServicePathSegmentMappingSerializer
    filterset_class = filtersets.ServicePathSegmentMappingFilterSet
