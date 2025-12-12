from netbox.api.routers import NetBoxRouter

from . import views

app_name = "cesnet_service_path_plugin"
router = NetBoxRouter()
router.register("segments", views.SegmentViewSet)
router.register("service-paths", views.ServicePathViewSet)
router.register("service-path-segment-mappings", views.ServicePathSegmentMappingViewSet)
router.register("segment-circuit-mappings", views.SegmentCircuitMappingViewSet)
router.register("contract-info", views.ContractInfoViewSet)

# Type-specific technical data endpoints
router.register("dark-fiber-data", views.DarkFiberSegmentDataViewSet)
router.register("optical-spectrum-data", views.OpticalSpectrumSegmentDataViewSet)
router.register("ethernet-service-data", views.EthernetServiceSegmentDataViewSet)


urlpatterns = router.urls
