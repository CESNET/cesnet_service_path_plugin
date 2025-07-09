from circuits.tables import CircuitTable
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from netbox.views import generic
import json

from cesnet_service_path_plugin.filtersets import SegmentFilterSet
from cesnet_service_path_plugin.forms import SegmentFilterForm, SegmentForm
from cesnet_service_path_plugin.models import (
    Segment,
    ServicePath,
    ServicePathSegmentMapping,
)
from cesnet_service_path_plugin.tables import SegmentTable, ServicePathTable
from cesnet_service_path_plugin.utils import export_segment_paths_as_geojson


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


# New view for downloading segment path as GeoJSON
def segment_geojson_download(request, pk):
    """
    Download segment path as GeoJSON file
    """
    segment = get_object_or_404(Segment, pk=pk)

    if not segment.has_path_data():
        return HttpResponse(
            json.dumps({"error": "No path data available for this segment"}),
            content_type="application/json",
            status=404,
        )

    # Use the existing utility function to export as GeoJSON
    geojson_data = export_segment_paths_as_geojson([segment])

    response = HttpResponse(geojson_data, content_type="application/json")
    response["Content-Disposition"] = f'attachment; filename="segment_{segment.pk}_{segment.name}.geojson"'

    return response
