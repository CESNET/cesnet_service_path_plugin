from circuits.tables import CircuitTable
from netbox.views import generic

from cesnet_service_path_plugin.filtersets import SegmentFilterSet
from cesnet_service_path_plugin.forms import SegmentFilterForm, SegmentForm
from cesnet_service_path_plugin.models import (
    Segment,
    ServicePath,
    ServicePathSegmentMapping,
)
from cesnet_service_path_plugin.tables import SegmentTable, ServicePathTable


class SegmentView(generic.ObjectView):
    queryset = Segment.objects.all()

    def get_extra_context(self, request, instance):
        circuits = instance.circuits.all()
        circuits_table = CircuitTable(circuits, exclude=())

        related_service_paths_ids = ServicePathSegmentMapping.objects.filter(segment=instance).values_list(
            "service_path_id", flat=True
        )
        service_paths = ServicePath.objects.filter(id__in=related_service_paths_ids)
        service_paths_table = ServicePathTable(service_paths, exclude=())
        return {
            "circuits_table": circuits_table,
            "sevice_paths_table": service_paths_table,
        }


class SegmentListView(generic.ObjectListView):
    queryset = Segment.objects.all()
    table = SegmentTable
    filterset = SegmentFilterSet
    filterset_form = SegmentFilterForm


class SegmentEditView(generic.ObjectEditView):
    queryset = Segment.objects.all()
    form = SegmentForm


class SegmentDeleteView(generic.ObjectDeleteView):
    queryset = Segment.objects.all()
