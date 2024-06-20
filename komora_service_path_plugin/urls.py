from django.urls import path
from netbox.views.generic import ObjectChangeLogView

from . import models, views

urlpatterns = (
    path("segments/", views.SegmentListView.as_view(), name="segment_list"),
    path("segments/add/", views.SegmentEditView.as_view(), name="segment_add"),
    path("segments/<int:pk>/", views.SegmentView.as_view(), name="segment"),
    path(
        "segments/<int:pk>/edit/", views.SegmentEditView.as_view(), name="segment_edit"
    ),
    path(
        "segments/<int:pk>/delete/",
        views.SegmentDeleteView.as_view(),
        name="segment_delete",
    ),
    path(
        "segments/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="segment_changelog",
        kwargs={"model": models.Segment},
    ),
    path(
        "service-paths/", views.ServicePathListView.as_view(), name="servicepath_list"
    ),
    path(
        "service-paths/add/",
        views.ServicePathEditView.as_view(),
        name="servicepath_add",
    ),
    path(
        "service-paths/<int:pk>/", views.ServicePathView.as_view(), name="servicepath"
    ),
    path(
        "service-paths/<int:pk>/edit/",
        views.ServicePathEditView.as_view(),
        name="servicepath_edit",
    ),
    path(
        "service-paths/<int:pk>/delete/",
        views.ServicePathDeleteView.as_view(),
        name="servicepath_delete",
    ),
    path(
        "service-paths/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="servicepath_changelog",
        kwargs={"model": models.ServicePath},
    ),
    path(
        "service-path-segment-mappings/",
        views.ServicePathSegmentMappingListView.as_view(),
        name="servicepathsegmentmapping_list",
    ),
    path(
        "service-path-segment-mappings/add/",
        views.ServicePathSegmentMappingEditView.as_view(),
        name="servicepathsegmentmapping_add",
    ),
    path(
        "service-path-segment-mappings/<int:pk>/",
        views.ServicePathSegmentMappingView.as_view(),
        name="servicepathsegmentmapping",
    ),
    path(
        "service-path-segment-mappings/<int:pk>/edit/",
        views.ServicePathSegmentMappingEditView.as_view(),
        name="servicepathsegmentmapping_edit",
    ),
    path(
        "service-path-segment-mappings/<int:pk>/delete/",
        views.ServicePathSegmentMappingDeleteView.as_view(),
        name="servicepathsegmentmapping_delete",
    ),
    path(
        "service-path-segment-mappings/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="servicepathsegmentmapping_changelog",
        kwargs={"model": models.ServicePathSegmentMapping},
    ),

    path(
        "service-path-circuit-mappings/",
        views.ServicePathCircuitMappingListView.as_view(),
        name="servicepathcircuitmapping_list",
    ),
    path(
        "service-path-circuit-mappings/add/",
        views.ServicePathCircuitMappingEditView.as_view(),
        name="servicepathcircuitmapping_add",
    ),
    path(
        "service-path-circuit-mappings/<int:pk>/",
        views.ServicePathCircuitMappingView.as_view(),
        name="servicepathcircuitmapping",
    ),
    path(
        "service-path-circuit-mappings/<int:pk>/edit/",
        views.ServicePathCircuitMappingEditView.as_view(),
        name="servicepathcircuitmapping_edit",
    ),
    path(
        "service-path-circuit-mappings/<int:pk>/delete/",
        views.ServicePathCircuitMappingDeleteView.as_view(),
        name="servicepathcircuitmapping_delete",
    ),
    path(
        "service-path-circuit-mappings/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="servicepathcircuitmapping_changelog",
        kwargs={"model": models.ServicePathCircuitMapping},
    ),

    path("segment-circuit-mappings/", views.SegmentCircuitMappingListView.as_view(),
         name="segmentcircuitmapping_list"),
    path("segment-circuit-mappings/add/",
         views.SegmentCircuitMappingEditView.as_view(), name="segmentcircuitmapping_add"),
    path("segment-circuit-mappings/<int:pk>/",
         views.SegmentCircuitMappingView.as_view(), name="segmentcircuitmapping"),
    path("segment-circuit-mappings/<int:pk>/edit/",
         views.SegmentCircuitMappingEditView.as_view(), name="segmentcircuitmapping_edit"),
    path("segment-circuit-mappings/<int:pk>/delete/",
         views.SegmentCircuitMappingDeleteView.as_view(), name="segmentcircuitmapping_delete"),
    path("segment-circuit-mappings/<int:pk>/changelog/", ObjectChangeLogView.as_view(),
         name="segmentcircuitmapping_changelog", kwargs={"model": models.SegmentCircuitMapping}),

    # TODO: HINT: Namapovat pridavani na circuits? - Ma to smysl?
    # path(
    #    "circuits/circuits/<int:pk>/segment_add/",
    #    views.SegmentCircuitEditView.as_view(),
    #    name="segmentcircuit_add",
    # ),
)
