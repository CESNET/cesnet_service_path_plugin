from circuits.tables import CircuitTable
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
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
        circuits_table = CircuitTable(circuits)
        circuits_table.configure(request)

        related_service_paths_ids = ServicePathSegmentMapping.objects.filter(segment=instance).values_list(
            "service_path_id", flat=True
        )
        service_paths = ServicePath.objects.filter(id__in=related_service_paths_ids)
        service_paths_table = ServicePathTable(service_paths)
        service_paths_table.configure(request)

        return {
            "circuits_table": circuits_table,
            "service_paths_table": service_paths_table,
        }


class SegmentListView(generic.ObjectListView):
    queryset = Segment.objects.all()
    table = SegmentTable
    filterset = SegmentFilterSet
    filterset_form = SegmentFilterForm
    template_name = "cesnet_service_path_plugin/segment_list.html"


class SegmentEditView(generic.ObjectEditView):
    queryset = Segment.objects.all()
    form = SegmentForm

    template_name = "cesnet_service_path_plugin/segment_edit.html"


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


# Map view for visualizing segment path
def segment_map_view(request, pk):
    """
    Display segment path on an interactive map with enhanced features
    """
    import json
    from django.shortcuts import get_object_or_404, render

    segment = get_object_or_404(Segment, pk=pk)

    # Prepare site data for endpoints

    has_fallback_line = False

    # Extract site coordinates if available
    try:
        site_a_data = {
            "name": str(segment.site_a),
            "lat": float(segment.site_a.latitude),
            "lng": float(segment.site_a.longitude),
        }
    except (ValueError, TypeError, AttributeError):
        site_a_data = None

    try:
        site_b_data = {
            "name": str(segment.site_b),
            "lat": float(segment.site_b.latitude),
            "lng": float(segment.site_b.longitude),
        }
    except (ValueError, TypeError, AttributeError):
        site_b_data = None

    # Check if we should show fallback line (when no geojson but sites have coordinates)
    if site_a_data and site_b_data:
        has_fallback_line = True

    # Prepare segment styling data
    segment_style = {"color": "#dc3545", "weight": 4, "opacity": 0.8}  # Red color for better visibility

    # Adjust styling based on status if needed
    # status_colors = {"Active": "#28a745", "Planned": "#ffc107", "Offline": "#dc3545"}

    # if hasattr(segment, "status") and hasattr(segment, "get_status_display"):
    #    segment_style["color"] = status_colors.get(segment.get_status_display(), "#dc3545")

    print("has path data:", segment.has_path_data())
    print("has fallback line:", has_fallback_line)

    context = {
        "object": segment,
        "segment": segment,
        "site_a_data": site_a_data,
        "site_b_data": site_b_data,
        "has_fallback_line": has_fallback_line,
        "segment_style": segment_style,
        "site_a_data_json": json.dumps(site_a_data) if site_a_data else "null",
        "site_b_data_json": json.dumps(site_b_data) if site_b_data else "null",
        "segment_style_json": json.dumps(segment_style),
    }
    return render(request, "cesnet_service_path_plugin/segment_map.html", context)


def segment_geojson_api(request, pk):
    """
    Return segment path as GeoJSON for map display
    """
    segment = get_object_or_404(Segment, pk=pk)

    if not segment.has_path_data():
        return JsonResponse({"type": "FeatureCollection", "features": []})

    # Create GeoJSON feature
    feature = {
        "type": "Feature",
        "geometry": json.loads(segment.get_path_geojson()),
        "properties": {
            "name": segment.name,
            "network_label": segment.network_label,
            "provider": str(segment.provider) if segment.provider else None,
            "status": segment.get_status_display(),
            "status_color": segment.get_status_color(),
            "path_length_km": float(segment.path_length_km) if segment.path_length_km else None,
            "install_date": segment.install_date.isoformat() if segment.install_date else None,
            "termination_date": segment.termination_date.isoformat() if segment.termination_date else None,
            "site_a": str(segment.site_a),
            "site_b": str(segment.site_b),
        },
    }

    geojson = {"type": "FeatureCollection", "features": [feature]}

    return JsonResponse(geojson)


# In cesnet_service_path_plugin/views/segment.py


class SegmentsMapView(generic.ObjectListView):
    """
    Display multiple segments on an interactive map with filtering support
    """

    queryset = Segment.objects.all()
    filterset = SegmentFilterSet
    filterset_form = SegmentFilterForm
    table = SegmentTable
    template_name = "cesnet_service_path_plugin/segments_map.html"

    def get_extra_context(self, request):
        context = super().get_extra_context(request)

        # Get filtered segments (same as the parent class does for table)
        filterset = self.filterset(request.GET, queryset=self.queryset)
        segments = filterset.qs

        # Limit the number of segments to prevent performance issues
        MAX_SEGMENTS = 500
        if segments.count() > MAX_SEGMENTS:
            segments = segments[:MAX_SEGMENTS]
            map_warning = f"Showing first {MAX_SEGMENTS} segments. Please use filters to narrow down results."
        else:
            map_warning = None

        # Prepare data for JavaScript
        segments_data = []
        map_bounds = {"minLat": None, "maxLat": None, "minLng": None, "maxLng": None}

        for segment in segments:
            # Extract site coordinates
            site_a_data = None
            site_b_data = None

            try:
                site_a_data = {
                    "name": str(segment.site_a),
                    "lat": float(segment.site_a.latitude),
                    "lng": float(segment.site_a.longitude),
                }
            except (ValueError, TypeError, AttributeError):
                pass

            try:
                site_b_data = {
                    "name": str(segment.site_b),
                    "lat": float(segment.site_b.latitude),
                    "lng": float(segment.site_b.longitude),
                }
            except (ValueError, TypeError, AttributeError):
                pass

            segment_data = {
                "id": segment.pk,
                "name": segment.name,
                "provider": str(segment.provider) if segment.provider else None,
                "provider_id": segment.provider.pk if segment.provider else None,
                "status": segment.get_status_display(),
                "status_color": segment.get_status_color(),
                # NEW: Add segment type information
                "segment_type": segment.get_segment_type_display(),
                "segment_type_color": segment.get_segment_type_color(),
                "path_length_km": float(segment.path_length_km) if segment.path_length_km else None,
                "site_a": site_a_data,
                "site_b": site_b_data,
                "has_path_data": segment.has_path_data(),
                "url": segment.get_absolute_url(),
                "map_url": f"/plugins/cesnet-service-path-plugin/segments/{segment.pk}/map/",
            }

            # Update map bounds
            for site_data in [site_a_data, site_b_data]:
                if site_data:
                    lat, lng = site_data["lat"], site_data["lng"]
                    if map_bounds["minLat"] is None or lat < map_bounds["minLat"]:
                        map_bounds["minLat"] = lat
                    if map_bounds["maxLat"] is None or lat > map_bounds["maxLat"]:
                        map_bounds["maxLat"] = lat
                    if map_bounds["minLng"] is None or lng < map_bounds["minLng"]:
                        map_bounds["minLng"] = lng
                    if map_bounds["maxLng"] is None or lng > map_bounds["maxLng"]:
                        map_bounds["maxLng"] = lng

            segments_data.append(segment_data)

        # Default center if no segments have coordinates
        if map_bounds["minLat"] is None:
            map_center = {"lat": 49.75, "lng": 15.5, "zoom": 7}  # Czech Republic center
        else:
            # Calculate center from bounds
            center_lat = (map_bounds["minLat"] + map_bounds["maxLat"]) / 2
            center_lng = (map_bounds["minLng"] + map_bounds["maxLng"]) / 2
            map_center = {"lat": center_lat, "lng": center_lng, "zoom": 7}

        # Add map-specific context
        context.update(
            {
                "segments_data": segments_data,
                "segments_data_json": json.dumps(segments_data),
                "map_bounds_json": json.dumps(map_bounds),
                "map_center_json": json.dumps(map_center),
                "segments_count": len(segments_data),
                "total_segments": Segment.objects.count(),
                "map_warning": map_warning,
                "api_url": self.request.build_absolute_uri("/plugins/cesnet-service-path-plugin/segments/map/api/"),
            }
        )

        return context


def segments_map_api(request):
    """
    API endpoint to return filtered segments as GeoJSON for map display
    """
    import json
    from django.http import JsonResponse

    # Use the same filterset as the table view
    filterset = SegmentFilterSet(request.GET, queryset=Segment.objects.all())
    segments = filterset.qs

    # Limit segments for performance
    MAX_SEGMENTS = 500
    if segments.count() > MAX_SEGMENTS:
        segments = segments[:MAX_SEGMENTS]

    features = []

    for segment in segments:
        if segment.has_path_data():
            # Add segment with actual path data
            try:
                geometry = json.loads(segment.get_path_geojson())
                feature = {
                    "type": "Feature",
                    "geometry": geometry,
                    "properties": {
                        "id": segment.pk,
                        "name": segment.name,
                        "network_label": segment.network_label,
                        "provider": str(segment.provider) if segment.provider else None,
                        "status": segment.get_status_display(),
                        "status_color": segment.get_status_color(),
                        # NEW: Add segment type information
                        "segment_type": segment.get_segment_type_display(),
                        "segment_type_color": segment.get_segment_type_color(),
                        "path_length_km": float(segment.path_length_km) if segment.path_length_km else None,
                        "site_a": str(segment.site_a),
                        "site_b": str(segment.site_b),
                        "url": segment.get_absolute_url(),
                        "map_url": f"/plugins/cesnet-service-path-plugin/segments/{segment.pk}/map/",
                        "type": "path",
                    },
                }
                features.append(feature)
            except Exception as e:
                print(f"Error processing segment {segment.pk}: {e}")
        else:
            # Add fallback line if both sites have coordinates
            try:
                site_a_lat = float(segment.site_a.latitude)
                site_a_lng = float(segment.site_a.longitude)
                site_b_lat = float(segment.site_b.latitude)
                site_b_lng = float(segment.site_b.longitude)

                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[site_a_lng, site_a_lat], [site_b_lng, site_b_lat]],
                    },
                    "properties": {
                        "id": segment.pk,
                        "name": segment.name,
                        "network_label": segment.network_label,
                        "provider": str(segment.provider) if segment.provider else None,
                        "status": segment.get_status_display(),
                        "status_color": segment.get_status_color(),
                        # NEW: Add segment type information
                        "segment_type": segment.get_segment_type_display(),
                        "segment_type_color": segment.get_segment_type_color(),
                        "path_length_km": float(segment.path_length_km) if segment.path_length_km else None,
                        "site_a": str(segment.site_a),
                        "site_b": str(segment.site_b),
                        "url": segment.get_absolute_url(),
                        "map_url": f"/plugins/cesnet-service-path-plugin/segments/{segment.pk}/map/",
                        "type": "fallback",
                    },
                }
                features.append(feature)
            except (ValueError, TypeError, AttributeError):
                # Skip segments without valid coordinates
                pass

    geojson = {"type": "FeatureCollection", "features": features}

    return JsonResponse(geojson)
