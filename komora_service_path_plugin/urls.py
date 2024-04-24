from django.urls import path
from netbox.views.generic import ObjectChangeLogView

from . import models, views

urlpatterns = (
    path(
        "segment-paths/",
        views.SegmentPathListView.as_view(),
        name="segmentpath_list"),
    path(
        "segment-paths/add/",
        views.SegmentPathEditView.as_view(),
        name="segmentpath_add"),
    path(
        "segment-paths/<int:pk>/",
        views.SegmentPathView.as_view(),
        name="segmentpath"),
    path(
        "segment-paths/<int:pk>/edit/",
        views.SegmentPathEditView.as_view(),
        name="segmentpath_edit"),
    path(
        "segment-paths/<int:pk>/delete/",
        views.SegmentPathDeleteView.as_view(),
        name="segmentpath_delete"),
    path(
        "segment-paths/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="segmentpath_changelog",
        kwargs={
            "model": models.SegmentPath},
    ),
    path(
        "service-paths/",
        views.ServicePathListView.as_view(),
        name="servicepath_list"),
    path(
        "service-paths/add/",
        views.ServicePathEditView.as_view(),
        name="servicepath_add"),
    path(
        "service-paths/<int:pk>/",
        views.ServicePathView.as_view(),
        name="servicepath"),
    path(
        "service-paths/<int:pk>/edit/",
        views.ServicePathEditView.as_view(),
        name="servicepath_edit"),
    path(
        "service-paths/<int:pk>/delete/",
        views.ServicePathDeleteView.as_view(),
        name="servicepath_delete"),
    path(
        "service-paths/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="servicepath_changelog",
        kwargs={
            "model": models.ServicePath},
    ),
)
