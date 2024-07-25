from circuits.models import Provider
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from netbox.plugins import PluginTemplateExtension

plugin_settings = settings.PLUGINS_CONFIG.get("komora_service_path_plugin", {})


class CircuitKomoraSegmentExtension(PluginTemplateExtension):
    model = "circuits.circuit"

    def full_width_page(self):
        return self.render(
            "komora_service_path_plugin/circuit_segments_extension.html",
        )


class TenantProviderExtension(PluginTemplateExtension):
    model = "tenancy.tenant"

    def left_page(self):
        provider = Provider.objects.filter(
            custom_field_data__tenant=self.context["object"].pk
        ).first()

        provider_circuits_count = provider.circuits.count() if provider else None

        return self.render(
            "komora_service_path_plugin/tenant_provider_extension.html",
            extra_context={
                "provider": provider,
                "provider_circuits_count": provider_circuits_count,
            },
        )


template_extensions = [CircuitKomoraSegmentExtension, TenantProviderExtension]
