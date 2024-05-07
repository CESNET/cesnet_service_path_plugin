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
)
