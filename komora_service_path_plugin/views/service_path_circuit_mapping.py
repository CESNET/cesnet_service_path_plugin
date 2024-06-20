from django.db.models import Count

from netbox.views import generic

# from ..filtersets import ServicePathCircuitMappingFilterSet
from komora_service_path_plugin.models import ServicePathCircuitMapping
from komora_service_path_plugin.forms import ServicePathCircuitMappingForm
from komora_service_path_plugin.tables import ServicePathCircuitMappingTable


class ServicePathCircuitMappingView(generic.ObjectView):
    queryset = ServicePathCircuitMapping.objects.all()


class ServicePathCircuitMappingListView(generic.ObjectListView):
    queryset = ServicePathCircuitMapping.objects.all()
    table = ServicePathCircuitMappingTable


class ServicePathCircuitMappingEditView(generic.ObjectEditView):
    queryset = ServicePathCircuitMapping.objects.all()
    form = ServicePathCircuitMappingForm


class ServicePathCircuitMappingDeleteView(generic.ObjectDeleteView):
    queryset = ServicePathCircuitMapping.objects.all()
