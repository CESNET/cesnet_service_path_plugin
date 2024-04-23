from netbox.api.metadata import ContentTypeMetadata
from netbox.api.viewsets import NetBoxModelViewSet

from ... import filtersets, models
from ..serializers import ServicePathSerializer


class ServicePathViewSet(NetBoxModelViewSet):
    metadata_class = ContentTypeMetadata
    queryset = models.ServicePath.objects.all()
    serializer_class = ServicePathSerializer
    filterset_class = filtersets.ServicePathFilterSet
