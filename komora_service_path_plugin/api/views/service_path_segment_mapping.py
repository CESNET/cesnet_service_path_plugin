from netbox.api.metadata import ContentTypeMetadata
from netbox.api.viewsets import NetBoxModelViewSet

from komora_service_path_plugin import filtersets, models
from komora_service_path_plugin.api.serializers import ServicePathSegmentMappingSerializer


class ServicePathSegmentMappingViewSet(NetBoxModelViewSet):
    metadata_class = ContentTypeMetadata
    queryset = models.ServicePathSegmentMapping.objects.all()
    serializer_class = ServicePathSegmentMappingSerializer
    filterset_class = filtersets.ServicePathSegmentMappingFilterSet
