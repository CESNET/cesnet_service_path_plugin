from django.db.models import Count

from netbox.views import generic

# from ..filtersets import ServicePathFilterSet
from komora_service_path_plugin.forms import ServicePathForm
from komora_service_path_plugin.models import ServicePath, ServicePathSegmentMapping
from komora_service_path_plugin.tables import ServicePathTable, ServicePathSegmentMappingTable
from circuits.tables import CircuitTable


class ServicePathView(generic.ObjectView):
    queryset = ServicePath.objects.all()

    def get_extra_context(self, request, instance):
        segment_mapping = ServicePathSegmentMapping.objects.filter(
            service_path=instance.id
        ).order_by("index")
        segment_mapping_table = ServicePathSegmentMappingTable(segment_mapping, exclude=("service_path", "id"))

        return {"segment_mapping_table": segment_mapping_table}


class ServicePathListView(generic.ObjectListView):
    queryset = ServicePath.objects.all()
    table = ServicePathTable

    actions = {
        'add': {},
        'edit': {},
        'import': {},
        'export': set(),
        'bulk_edit': {},
        'bulk_delete': {},
    }
