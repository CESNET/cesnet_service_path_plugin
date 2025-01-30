from netbox.views import generic

from komora_service_path_plugin.filtersets import ServicePathSegmentMappingFilterSet
from komora_service_path_plugin.forms import ServicePathSegmentMappingFilterForm, ServicePathSegmentMappingForm
from komora_service_path_plugin.models import ServicePathSegmentMapping
from komora_service_path_plugin.tables import ServicePathSegmentMappingTable


# List View
class ServicePathSegmentMappingListView(generic.ObjectListView):
    queryset = ServicePathSegmentMapping.objects.all()
    table = ServicePathSegmentMappingTable
    filterset = ServicePathSegmentMappingFilterSet
    filterset_form = ServicePathSegmentMappingFilterForm


# Detail View
class ServicePathSegmentMappingView(generic.ObjectView):
    queryset = ServicePathSegmentMapping.objects.all()
    template_name = "komora_service_path_plugin/servicepathsegmentmapping.html"


# Create/Edit View
class ServicePathSegmentMappingEditView(generic.ObjectEditView):
    queryset = ServicePathSegmentMapping.objects.all()
    form = ServicePathSegmentMappingForm
    # template_name = 'komora_service_path_plugin/servicepathsegmentmapping_edit.html'


# Delete View
class ServicePathSegmentMappingDeleteView(generic.ObjectDeleteView):
    queryset = ServicePathSegmentMapping.objects.all()
    # template_name = 'komora_service_path_plugin/servicepathsegmentmapping_delete.html'
