from circuits.tables import CircuitTable
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
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

    # Create a very simple, safe filename
    clean_name = slugify(segment.name)
    filename = f"segment_{segment.pk}_{clean_name}.geojson"

    # filename = f"segment_{segment.pk}.geojson"

    response = HttpResponse(geojson_data, content_type="application/octet-stream")

    # Simple, safe Content-Disposition header
    response["Content-Disposition"] = f"attachment; filename={filename}"
    response["Cache-Control"] = "no-cache"

    return response


# New view for clearing segment path data
def segment_path_clear(request, pk):
    """
    Clear path data from a segment
    """
    segment = get_object_or_404(Segment, pk=pk)

    if not segment.has_path_data():
        messages.warning(request, "This segment doesn't have any path data to clear.")
        return redirect(segment.get_absolute_url())

    if request.method == "POST":
        # Clear all path-related fields
        segment.path_geometry = None
        segment.path_source_format = None
        segment.path_length_km = None
        segment.path_notes = ""
        segment.save()

        messages.success(request, f"Path data has been cleared from segment '{segment.name}'.")
        return redirect(segment.get_absolute_url())

    # For GET requests, show confirmation page
    return render(request, "cesnet_service_path_plugin/segment_path_clear_confirm.html", {"object": segment})
