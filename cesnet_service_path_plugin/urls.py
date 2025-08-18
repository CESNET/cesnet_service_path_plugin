from django.urls import include, path
from utilities.urls import get_model_urls

from cesnet_service_path_plugin.views import (
    SegmentCircuitMappingDeleteView,
    SegmentCircuitMappingEditView,
    SegmentCircuitMappingListView,
    SegmentCircuitMappingView,
    SegmentDeleteView,
    SegmentEditView,
    SegmentListView,
    SegmentView,
    ServicePathDeleteView,
    ServicePathEditView,
    ServicePathListView,
    ServicePathSegmentMappingDeleteView,
    ServicePathSegmentMappingEditView,
    ServicePathSegmentMappingListView,
    ServicePathSegmentMappingView,
    ServicePathView,
    segment_geojson_download,
    segment_path_clear,
    segment_map_view,
    segment_geojson_api,
    SegmentsMapView,
    segments_map_api,
)

urlpatterns = (
    # Segment paths
    path("segments/", SegmentListView.as_view(), name="segment_list"),
    path("segments/add/", SegmentEditView.as_view(), name="segment_add"),
    path("segments/<int:pk>/", SegmentView.as_view(), name="segment"),
    path("segments/<int:pk>/edit/", SegmentEditView.as_view(), name="segment_edit"),
    path("segments/<int:pk>/delete/", SegmentDeleteView.as_view(), name="segment_delete"),
    # NEW: Map views
    path("segments/<int:pk>/map/", segment_map_view, name="segment_map"),
    path("segments/<int:pk>/geojson-api/", segment_geojson_api, name="segment_geojson_api"),
    # Adds Changelog, Journal, and Attachment tabs to the Segment view
    path(
        "segments/",
        include(get_model_urls("cesnet_service_path_plugin", "segment", detail=False)),
    ),
    path(
        "segments/<int:pk>/",
        include(get_model_urls("cesnet_service_path_plugin", "segment")),
    ),
    # GeoJSON download endpoint
    path("segments/<int:pk>/geojson/", segment_geojson_download, name="segment_geojson_download"),
    path("segments/<int:pk>/clear-path/", segment_path_clear, name="segment_path_clear"),
    # Segments map views
    path("segments/map/", SegmentsMapView.as_view(), name="segments_map"),
    path("segments/map/api/", segments_map_api, name="segments_map_api"),
    # ServicePath paths
    path("service-paths/", ServicePathListView.as_view(), name="servicepath_list"),
    path("service-paths/add/", ServicePathEditView.as_view(), name="servicepath_add"),
    path("service-paths/<int:pk>/", ServicePathView.as_view(), name="servicepath"),
    path(
        "service-paths/<int:pk>/edit/",
        ServicePathEditView.as_view(),
        name="servicepath_edit",
    ),
    path(
        "service-paths/<int:pk>/delete/",
        ServicePathDeleteView.as_view(),
        name="servicepath_delete",
    ),
    path(
        "service_paths/",
        include(get_model_urls("cesnet_service_path_plugin", "servicepath", detail=False)),
    ),
    path(
        "service_paths/<int:pk>/",
        include(get_model_urls("cesnet_service_path_plugin", "servicepath")),
    ),
    # ServicePathSegmentMapping paths
    path(
        "service-path-segment-mappings/",
        ServicePathSegmentMappingListView.as_view(),
        name="servicepathsegmentmapping_list",
    ),
    path(
        "service-path-segment-mappings/add/",
        ServicePathSegmentMappingEditView.as_view(),
        name="servicepathsegmentmapping_add",
    ),
    path(
        "service-path-segment-mappings/<int:pk>/",
        ServicePathSegmentMappingView.as_view(),
        name="servicepathsegmentmapping",
    ),
    path(
        "service-path-segment-mappings/<int:pk>/edit/",
        ServicePathSegmentMappingEditView.as_view(),
        name="servicepathsegmentmapping_edit",
    ),
    path(
        "service-path-segment-mappings/<int:pk>/delete/",
        ServicePathSegmentMappingDeleteView.as_view(),
        name="servicepathsegmentmapping_delete",
    ),
    path(
        "service-path-segment-mappings/",
        include(get_model_urls("cesnet_service_path_plugin", "servicepathsegmentmapping", detail=False)),
    ),
    path(
        "service-path-segment-mappings/<int:pk>/",
        include(get_model_urls("cesnet_service_path_plugin", "servicepathsegmentmapping")),
    ),
    # SegmentCircuitMapping paths
    path(
        "segment-circuit-mappings/",
        SegmentCircuitMappingListView.as_view(),
        name="segmentcircuitmapping_list",
    ),
    path(
        "segment-circuit-mappings/add/",
        SegmentCircuitMappingEditView.as_view(),
        name="segmentcircuitmapping_add",
    ),
    path(
        "segment-circuit-mappings/<int:pk>/",
        SegmentCircuitMappingView.as_view(),
        name="segmentcircuitmapping",
    ),
    path(
        "segment-circuit-mappings/<int:pk>/edit/",
        SegmentCircuitMappingEditView.as_view(),
        name="segmentcircuitmapping_edit",
    ),
    path(
        "segment-circuit-mappings/<int:pk>/delete/",
        SegmentCircuitMappingDeleteView.as_view(),
        name="segmentcircuitmapping_delete",
    ),
    path(
        "segment-circuit-mappings/",
        include(get_model_urls("cesnet_service_path_plugin", "segmentcircuitmapping", detail=False)),
    ),
    path(
        "segment-circuit-mappings/<int:pk>/",
        include(get_model_urls("cesnet_service_path_plugin", "segmentcircuitmapping")),
    ),
)
