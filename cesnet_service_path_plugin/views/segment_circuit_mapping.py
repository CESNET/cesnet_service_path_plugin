from netbox.views import generic

from cesnet_service_path_plugin.filtersets import SegmentCircuitMappingFilterSet
from cesnet_service_path_plugin.forms import SegmentCircuitMappingForm
from cesnet_service_path_plugin.models import SegmentCircuitMapping
from cesnet_service_path_plugin.tables import SegmentCircuitMappingTable


class SegmentCircuitMappingListView(generic.ObjectListView):
    queryset = SegmentCircuitMapping.objects.all()
    table = SegmentCircuitMappingTable
    filterset = SegmentCircuitMappingFilterSet


# From Circuit to Segment
# Create/Edit View
class SegmentCircuitMappingEditView(generic.ObjectEditView):
    queryset = SegmentCircuitMapping.objects.all()
    form = SegmentCircuitMappingForm


class SegmentCircuitMappingDeleteView(generic.ObjectDeleteView):
    queryset = SegmentCircuitMapping.objects.all()


class SegmentCircuitMappingView(generic.ObjectView):
    queryset = SegmentCircuitMapping.objects.all()
    template_name = "cesnet_service_path_plugin/segmentcircuitmapping.html"
