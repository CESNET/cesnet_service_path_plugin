from netbox.views import generic

from komora_service_path_plugin.models import ServicePathSegmentMapping
from komora_service_path_plugin.tables import ServicePathSegmentMappingTable


class ServicePathSegmentMappingListView(generic.ObjectListView):
    queryset = ServicePathSegmentMapping.objects.all()
    table = ServicePathSegmentMappingTable
    actions = {
        'add': {},
        'edit': {},
        'import': {},
        'export': set(),
        'bulk_edit': {},
        'bulk_delete': {},
    }