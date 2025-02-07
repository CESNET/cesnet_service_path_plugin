from django.urls import path
from netbox.views.generic import ObjectChangeLogView, ObjectJournalView

from cesnet_service_path_plugin.models import (
    Segment,
    SegmentCircuitMapping,
    ServicePath,
    ServicePathSegmentMapping,
)
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
)

urlpatterns = (
    # Segment paths
    path("segments/", SegmentListView.as_view(), name="segment_list"),
    path("segments/add/", SegmentEditView.as_view(), name="segment_add"),
    path("segments/<int:pk>/", SegmentView.as_view(), name="segment"),
    path("segments/<int:pk>/edit/", SegmentEditView.as_view(), name="segment_edit"),
    path(
        "segments/<int:pk>/delete/", SegmentDeleteView.as_view(), name="segment_delete"
    ),
    path(
        "segments/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="segment_changelog",
        kwargs={"model": Segment},
    ),
    path(
        "segments/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="segment_journal",
        kwargs={"model": Segment},  # Add this line to specify the model
    ),
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
        "service-paths/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="servicepath_changelog",
        kwargs={"model": ServicePath},
    ),
    path(
        "service-paths/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="servicepath_journal",
        kwargs={"model": ServicePath},  # Add this line to specify the model
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
        "service-path-segment-mappings/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="servicepathsegmentmapping_changelog",
        kwargs={"model": ServicePathSegmentMapping},
    ),
    path(
        "service-path-segment-mappings/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="servicepathsegmentmapping_journal",
        kwargs={
            "model": ServicePathSegmentMapping
        },  # Add this line to specify the model
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
        "segment-circuit-mappings/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="segmentcircuitmapping_changelog",
        kwargs={"model": SegmentCircuitMapping},
    ),
    path(
        "segment-circuit-mappings/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="segmentcircuitmapping_journal",
        kwargs={"model": SegmentCircuitMapping},  # Add this line to specify the model
    ),
)
