from netbox.api.metadata import ContentTypeMetadata
from netbox.api.viewsets import NetBoxModelViewSet

from komora_service_path_plugin import filtersets, models
from komora_service_path_plugin.api.serializers import ServicePathCircuitMappingSerializer


class ServicePathCircuitMappingViewSet(NetBoxModelViewSet):
    metadata_class = ContentTypeMetadata
    queryset = models.ServicePathCircuitMapping.objects.all()
    serializer_class = ServicePathCircuitMappingSerializer
    filterset_class = filtersets.ServicePathCircuitMappingFilterSet
