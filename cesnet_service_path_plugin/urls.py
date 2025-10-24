from django.urls import include, path
from utilities.urls import get_model_urls

from cesnet_service_path_plugin.views import (
    SegmentsMapView,
    segment_geojson_api,
    segment_geojson_download,
    segment_map_view,
    segment_path_clear,
    segments_map_api,
)

urlpatterns = (
    path("segments/<int:pk>/map/", segment_map_view, name="segment_map"),
    path("segments/<int:pk>/geojson-api/", segment_geojson_api, name="segment_geojson_api"),
    # GeoJSON download endpoint
    path("segments/<int:pk>/geojson/", segment_geojson_download, name="segment_geojson_download"),
    path("segments/<int:pk>/clear-path/", segment_path_clear, name="segment_path_clear"),
    # Segments map views
    path("segments/map/", SegmentsMapView.as_view(), name="segments_map"),
    path("segments/map/api/", segments_map_api, name="segments_map_api"),
    # All class-based views (CRUD, bulk, custom classes) are registered via @register_model_view
    # and will be automatically included by get_model_urls
    path(
        "segments/",
        include(get_model_urls("cesnet_service_path_plugin", "segment", detail=False)),
    ),
    path(
        "segments/<int:pk>/",
        include(get_model_urls("cesnet_service_path_plugin", "segment")),
    ),
    # ServicePath views
    path(
        "service-paths/",
        include(get_model_urls("cesnet_service_path_plugin", "servicepath", detail=False)),
    ),
    path(
        "service-paths/<int:pk>/",
        include(get_model_urls("cesnet_service_path_plugin", "servicepath")),
    ),
    # ServicePathSegmentMapping views
    path(
        "service-path-segment-mappings/",
        include(get_model_urls("cesnet_service_path_plugin", "servicepathsegmentmapping", detail=False)),
    ),
    path(
        "service-path-segment-mappings/<int:pk>/",
        include(get_model_urls("cesnet_service_path_plugin", "servicepathsegmentmapping")),
    ),
    # SegmentCircuitMapping views
    path(
        "segment-circuit-mappings/",
        include(get_model_urls("cesnet_service_path_plugin", "segmentcircuitmapping", detail=False)),
    ),
    path(
        "segment-circuit-mappings/<int:pk>/",
        include(get_model_urls("cesnet_service_path_plugin", "segmentcircuitmapping")),
    ),
    # SegmentFinancialInfo views
    path(
        "segment-financial-info/",
        include(get_model_urls("cesnet_service_path_plugin", "segmentfinancialinfo", detail=False)),
    ),
    path(
        "segment-financial-info/<int:pk>/",
        include(get_model_urls("cesnet_service_path_plugin", "segmentfinancialinfo")),
    ),
)
