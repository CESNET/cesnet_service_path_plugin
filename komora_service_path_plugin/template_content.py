from circuits.models import Circuit
from django.conf import settings
from komora_service_path_plugin.models import (
    SegmentCircuitMapping,
    ServicePathCircuitMapping,
    ServicePathSegmentMapping,
)
from komora_service_path_plugin.tables import (
    SegmentCircuitMappingTable,
    ServicePathCircuitMappingTable,
    ServicePathSegmentMappingTable,
)
from netbox.plugins import PluginTemplateExtension
from netbox.views import generic
from utilities.views import ViewTab, register_model_view

plugin_settings = settings.PLUGINS_CONFIG.get("komora_service_path_plugin", {})


class SegmentMappingListToServicePath(PluginTemplateExtension):
    model = "komora_service_path_plugin.servicepath"
    exclude = ("service_path", "id")

    def full_width_page(self):
        service_path = self.context["object"]
        segment_mapping = ServicePathSegmentMapping.objects.filter(
            service_path=service_path.id
        ).order_by("index")
        segment_mapping_table = ServicePathSegmentMappingTable(
            segment_mapping, exclude=self.exclude
        )

        return self.render(
            "komora_service_path_plugin/segment_mapping_include.html",
            extra_context={
                "segment_mapping": segment_mapping,
                "related_session_table": segment_mapping_table,
            },
        )


template_extensions = [
    SegmentMappingListToServicePath,
]


@register_model_view(Circuit, name='circuit-komora-service-path', path='circuit-komora-service-path')
class CircuitKomoraServicePathView(generic.ObjectView):
    template_name = "komora_service_path_plugin/circuit_komora_service_paths_tab.html"
    queryset = Circuit.objects.all()

    tab = ViewTab(
        label='Komora Service Paths',
        # badge=lambda obj: Stuff.objects.filter(site=obj).count(),
        # permission='myplugin.view_stuff'
    )

    def get_extra_context(self, request, instance):
        segment_mapping = SegmentCircuitMapping.objects.filter(
            circuit=instance.id)
        segment_mapping_table = SegmentCircuitMappingTable(
            segment_mapping, exclude=())

        service_path_mapping = ServicePathCircuitMapping.objects.filter(
            circuit=instance.id)
        service_path_mapping_table = ServicePathCircuitMappingTable(
            service_path_mapping, exclude=())

        return {"segment_mapping_table": segment_mapping_table, "service_path_mapping_table": service_path_mapping_table}
