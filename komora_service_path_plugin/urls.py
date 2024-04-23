from django.urls import path
from netbox.views.generic import ObjectChangeLogView

from . import models, views

'''
urlpatterns = (
    path("komora-service-path-plugins/", views.komora_service_path_pluginListView.as_view(), name="komoraservicepathplugin_list"),
    path("komora-service-path-plugins/add/", views.komora_service_path_pluginEditView.as_view(), name="komoraservicepathplugin_add"),
    path("komora-service-path-plugins/<int:pk>/", views.komora_service_path_pluginView.as_view(), name="komoraservicepathplugin"),
    path("komora-service-path-plugins/<int:pk>/edit/", views.komora_service_path_pluginEditView.as_view(), name="komoraservicepathplugin_edit"),
    path("komora-service-path-plugins/<int:pk>/delete/", views.komora_service_path_pluginDeleteView.as_view(), name="komoraservicepathplugin_delete"),
    path(
        "komora-service-path-plugins/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="komoraservicepathplugin_changelog",
        kwargs={"model": models.komora_service_path_plugin},
    ),
)
'''
