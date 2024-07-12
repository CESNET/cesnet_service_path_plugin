from komora_service_path_plugin.filtersets import SegmentCircuitMappingFilterSet
from komora_service_path_plugin.forms import SegmentCircuitMappingForm
from komora_service_path_plugin.models import SegmentCircuitMapping
from komora_service_path_plugin.tables import SegmentCircuitMappingTable
from netbox.views import generic


class SegmentCircuitMappingListView(generic.ObjectListView):
    queryset = SegmentCircuitMapping.objects.all()
    table = SegmentCircuitMappingTable
    filterset = SegmentCircuitMappingFilterSet

    actions = {}


class SegmentCircuitMappingEditView(generic.ObjectEditView):
    queryset = SegmentCircuitMapping.objects.all()
    form = SegmentCircuitMappingForm

    def alter_object(self, instance, request, args, kwargs):
        instance.circuit_id = request.GET.get('circuit_id')
        return instance

    def get_extra_addanother_params(self, request):
        return {
            'circuit_id': request.GET.get('circuit_id')
        }


class SegmentCircuitMappingDeleteView(generic.ObjectDeleteView):
    queryset = SegmentCircuitMapping.objects.all()
