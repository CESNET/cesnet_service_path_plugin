from netbox.api.routers import NetBoxRouter

from . import views

app_name = "cesnet_service_path_plugin"
router = NetBoxRouter()
router.register("segments", views.SegmentViewSet)
router.register("service-paths", views.ServicePathViewSet)
router.register("service-path-segment-mappings", views.ServicePathSegmentMappingViewSet)
router.register("segment-circuit-mappings", views.SegmnetCircuitMappingViewSet)

urlpatterns = router.urls
