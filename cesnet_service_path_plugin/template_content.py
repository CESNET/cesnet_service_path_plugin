import django_tables2
from circuits.models import Provider
from circuits.tables import CircuitTable
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from netbox.plugins import PluginTemplateExtension
from utilities.tables import register_table_column

from cesnet_service_path_plugin.models import Segment

plugin_settings = settings.PLUGINS_CONFIG.get("cesnet_service_path_plugin", {})

# Extra Views


class CircuitKomoraSegmentExtension(PluginTemplateExtension):
    models = ["circuits.circuit"]

    def full_width_page(self):
        return self.render(
            "cesnet_service_path_plugin/circuit_segments_extension.html",
        )


class ProviderSegmentExtension(PluginTemplateExtension):
    models = ["circuits.provider"]

    def full_width_page(self):
        return self.render(
            "cesnet_service_path_plugin/provider_segments_extension.html",
        )


class SiteSegmentExtension(PluginTemplateExtension):
    models = ["dcim.site"]

    def full_width_page(self):
        return self.render(
            "cesnet_service_path_plugin/site_segments_extension.html",
        )


class LocationSegmentExtension(PluginTemplateExtension):
    models = ["dcim.location"]

    def full_width_page(self):
        return self.render(
            "cesnet_service_path_plugin/location_segments_extension.html",
        )


class TenantProviderExtension(PluginTemplateExtension):
    models = ["tenancy.tenant"]

    def left_page(self):
        provider = Provider.objects.filter(
            custom_field_data__tenant=self.context["object"].pk
        ).first()

        provider_circuits_count = provider.circuits.count() if provider else None
        provider_segments_count = (
            Segment.objects.filter(provider_id=provider.id).count()
            if provider
            else None
        )

        return self.render(
            "cesnet_service_path_plugin/tenant_provider_extension.html",
            extra_context={
                "provider": provider,
                "provider_circuits_count": provider_circuits_count,
                "provider_segments_count": provider_segments_count,
            },
        )


template_extensions = [
    CircuitKomoraSegmentExtension,
    TenantProviderExtension,
    ProviderSegmentExtension,
    SiteSegmentExtension,
    LocationSegmentExtension,
]

# Extra Columns

circuit_segments = django_tables2.TemplateColumn(
    verbose_name=_("Segments"),
    template_name="cesnet_service_path_plugin/circuit_segments_template_column.html",
    orderable=False,
    linkify=False,
)

register_table_column(circuit_segments, "circuit_segments", CircuitTable)
