from netbox.views import generic

from komora_service_path_plugin.models import ServicePathSegmentMapping
from komora_service_path_plugin.tables import ServicePathSegmentMappingTable
from komora_service_path_plugin.filtersets import ServicePathSegmentMappingFilterSet
from komora_service_path_plugin.forms import ServicePathSegmentMappingFilterForm


class ServicePathSegmentMappingListView(generic.ObjectListView):
    queryset = ServicePathSegmentMapping.objects.all()
    table = ServicePathSegmentMappingTable
    filterset = ServicePathSegmentMappingFilterSet
    filterset_form = ServicePathSegmentMappingFilterForm
    actions = {
        'add': {},
        'edit': {},
        'import': {},
        'export': set(),
        'bulk_edit': {},
        'bulk_delete': {},
    }
