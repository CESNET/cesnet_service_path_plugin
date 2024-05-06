from netbox.api.routers import NetBoxRouter

from . import views

app_name = 'komora_service_path_plugin'
router = NetBoxRouter()
router.register('segments', views.SegmentViewSet)
router.register('service-paths', views.ServicePathViewSet)

urlpatterns = router.urls
