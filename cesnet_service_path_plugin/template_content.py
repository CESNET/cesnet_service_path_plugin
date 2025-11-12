import django_tables2
import json
from circuits.models import Provider
from circuits.tables import CircuitTable
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from netbox.plugins import PluginTemplateExtension
from utilities.tables import register_table_column

from cesnet_service_path_plugin.models import Segment, ServicePathSegmentMapping, ServicePath
from cesnet_service_path_plugin.utils import build_service_path_topology, build_segment_topology
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

plugin_settings = settings.PLUGINS_CONFIG.get("cesnet_service_path_plugin", {})


# Extra Views


class CircuitSegmentExtension(PluginTemplateExtension):
    models = ["circuits.circuit"]

    def full_width_page(self):
        circuit = self.context["object"]

        # Get the first segment associated with this circuit
        try:
            segment = circuit.segment_set.first()
        except AttributeError:
            segment = None

        # Initialize topology data
        topology_data = None
        topology_title = None
        topologies = {}

        if segment:
            # Check if segment is part of any service path
            service_paths = ServicePathSegmentMapping.objects.filter(segment=segment).all()
            if service_paths:
                for sp in service_paths:
                    # get data from service path model
                    sp_data = ServicePath.objects.filter(id=sp.service_path_id).first()

                    topology_title = f"Service Path {sp_data.name}"
                    topology_data = build_service_path_topology(sp_data)
                    topologies[topology_title] = json.dumps(topology_data)
            else:
                topology_title = f"Segment  {segment.name}"
                topology_data = build_segment_topology(segment=segment)
                topologies[topology_title] = json.dumps(topology_data)

        return self.render(
            "cesnet_service_path_plugin/circuit_segments_extension.html",
            extra_context={
                "segment": segment,
                "topologies": topologies,
            },
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
        provider = Provider.objects.filter(custom_field_data__tenant=self.context["object"].pk).first()

        provider_circuits_count = provider.circuits.count() if provider else None
        provider_segments_count = Segment.objects.filter(provider_id=provider.id).count() if provider else None

        return self.render(
            "cesnet_service_path_plugin/tenant_provider_extension.html",
            extra_context={
                "provider": provider,
                "provider_circuits_count": provider_circuits_count,
                "provider_segments_count": provider_segments_count,
            },
        )


template_extensions = [
    CircuitSegmentExtension,
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
