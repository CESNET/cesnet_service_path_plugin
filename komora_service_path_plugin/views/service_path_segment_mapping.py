from netbox.views import generic

from komora_service_path_plugin.models import ServicePathSegmentMapping
from komora_service_path_plugin.forms import ServicePathSegmentMappingForm
from komora_service_path_plugin.tables import ServicePathSegmentMappingTable


class ServicePathSegmentMappingListView(generic.ObjectListView):
    queryset = ServicePathSegmentMapping.objects.all()
    table = ServicePathSegmentMappingTable


class ServicePathSegmentMappingEditView(generic.ObjectEditView):
    queryset = ServicePathSegmentMapping.objects.all()
    form = ServicePathSegmentMappingForm


class ServicePathSegmentMappingDeleteView(generic.ObjectDeleteView):
    queryset = ServicePathSegmentMapping.objects.all()
