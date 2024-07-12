from django.conf import settings
from netbox.plugins import PluginTemplateExtension

plugin_settings = settings.PLUGINS_CONFIG.get("komora_service_path_plugin", {})


class CircuitKomoraSegmentExtension(PluginTemplateExtension):
    model = "circuits.circuit"

    def full_width_page(self):
        return self.render(
            "komora_service_path_plugin/circuit_segments_extension.html",
        )


template_extensions = [CircuitKomoraSegmentExtension]
