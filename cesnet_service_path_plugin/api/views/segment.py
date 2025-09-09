from netbox.api.metadata import ContentTypeMetadata
from netbox.api.viewsets import NetBoxModelViewSet

from cesnet_service_path_plugin.models import Segment
from cesnet_service_path_plugin.filtersets import SegmentFilterSet
from cesnet_service_path_plugin.api.serializers import SegmentSerializer, SegmentDetailSerializer


class SegmentViewSet(NetBoxModelViewSet):
    metadata_class = ContentTypeMetadata
    queryset = Segment.objects.all()
    filterset_class = SegmentFilterSet

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == "retrieve":
            pathdata = self.request.query_params.get("pathdata", "false").lower() == "true"
            if pathdata:
                return SegmentDetailSerializer

        # Use the updated SegmentSerializer for all other actions (including create/update)
        return SegmentSerializer
