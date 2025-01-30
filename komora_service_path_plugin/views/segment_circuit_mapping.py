from netbox.views import generic

from komora_service_path_plugin.filtersets import SegmentCircuitMappingFilterSet
from komora_service_path_plugin.forms import SegmentCircuitMappingForm
from komora_service_path_plugin.models import SegmentCircuitMapping
from komora_service_path_plugin.tables import SegmentCircuitMappingTable


class SegmentCircuitMappingListView(generic.ObjectListView):
    queryset = SegmentCircuitMapping.objects.all()
    table = SegmentCircuitMappingTable
    filterset = SegmentCircuitMappingFilterSet


# From Circuit to Segment
# Create/Edit View
class SegmentCircuitMappingEditView(generic.ObjectEditView):
    queryset = SegmentCircuitMapping.objects.all()
    form = SegmentCircuitMappingForm
    # template_name = 'komora_service_path_plugin/servicepathsegmentmapping_edit.html'


class SegmentCircuitMappingDeleteView(generic.ObjectDeleteView):
    queryset = SegmentCircuitMapping.objects.all()


class SegmentCircuitMappingView(generic.ObjectView):
    queryset = SegmentCircuitMapping.objects.all()
    template_name = "komora_service_path_plugin/segmentcircuitmapping.html"

    def get_extra_context(self, request, instance):
        return {"circuit": instance.circuit, "segment": instance.segment}
