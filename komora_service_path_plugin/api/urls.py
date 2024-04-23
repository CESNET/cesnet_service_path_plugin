from netbox.api.routers import NetBoxRouter

from . import views

app_name = 'komora_service_path_plugin'
router = NetBoxRouter()
router.register('segment-path', views.SegmentPathViewSet)
router.register('service-path', views.ServicePathViewSet)

urlpatterns = router.urls
