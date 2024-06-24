from komora_service_path_plugin.forms import ServicePathCircuitMappingForm
from komora_service_path_plugin.models import ServicePathCircuitMapping
from komora_service_path_plugin.tables import ServicePathCircuitMappingTable
from netbox.views import generic


class ServicePathCircuitMappingListView(generic.ObjectListView):
    queryset = ServicePathCircuitMapping.objects.all()
    table = ServicePathCircuitMappingTable
    actions = {}


class ServicePathCircuitMappingEditView(generic.ObjectEditView):
    queryset = ServicePathCircuitMapping.objects.all()
    form = ServicePathCircuitMappingForm

    def alter_object(self, instance, request, args, kwargs):
        instance.circuit_id = request.GET.get('circuit_id')
        return instance

    def get_extra_addanother_params(self, request):
        return {
            'circuit_id': request.GET.get('circuit_id')
        }


class ServicePathCircuitMappingDeleteView(generic.ObjectDeleteView):
    queryset = ServicePathCircuitMapping.objects.all()
