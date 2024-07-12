from django.urls import path
from komora_service_path_plugin import models, views
from netbox.views.generic import ObjectChangeLogView

urlpatterns = (
    path("segments/", views.SegmentListView.as_view(), name="segment_list"),
    path("segments/<int:pk>/", views.SegmentView.as_view(), name="segment"),
    path("segments/<int:pk>/edit",
         views.SegmentEditView.as_view(), name="segment_edit"),
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
        "service-paths/<int:pk>/", views.ServicePathView.as_view(), name="servicepath"
    ),
    path(
        "service-paths/<int:pk>/edit", views.ServicePathEditView.as_view(), name="servicepath_edit"
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

    path("segment-circuit-mappings/", views.SegmentCircuitMappingListView.as_view(),
         name="segmentcircuitmapping_list"),
    path("segment-circuit-mappings/add/",
         views.SegmentCircuitMappingEditView.as_view(), name="segmentcircuitmapping_add"),
    path("segment-circuit-mappings/<int:pk>/delete/",
         views.SegmentCircuitMappingDeleteView.as_view(), name="segmentcircuitmapping_delete"),

)
