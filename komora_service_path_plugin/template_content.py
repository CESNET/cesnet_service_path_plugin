from circuits.models import Circuit, CircuitTermination
from circuits.tables import CircuitTable
from dcim.models import Device, Interface
from ipam.models import IPAddress, Prefix, VRF
from netbox.plugins import PluginTemplateExtension
from netbox.views import generic
from utilities.views import ViewTab, register_model_view
from django.conf import settings
from django.db.models import F

from komora_service_path_plugin.filtersets import (
    SegmentFilterSet,
    ServicePathFilterSet,
    ServicePathSegmentMappingFilterSet,
    ServicePathCircuitMappingFilterSet,
    SegmentCircuitMappingFilterSet
)
from komora_service_path_plugin.models import (
    Segment,
    ServicePath,
    ServicePathSegmentMapping,
    ServicePathCircuitMapping,
    SegmentCircuitMapping
)
from komora_service_path_plugin.tables import (
    SegmentTable,
    ServicePathSegmentMappingTable,
    ServicePathTable,
    ServicePathCircuitMappingTable,
    SegmentCircuitMappingTable
)


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


class ServicePathToCircuit(PluginTemplateExtension):
    model = "circuits.circuit"
    exclude = ()

    def full_width_page(self):
        circuit = self.context["object"]

        service_path_ids = ServicePathCircuitMapping.objects.filter(
            circuit=circuit.id
        ).values_list("service_path_id", flat=True)

        service_paths = ServicePath.objects.filter(
            id__in=service_path_ids).all()
        service_path_table = ServicePathTable(
            service_paths, exclude=self.exclude
        )

        return self.render(
            "komora_service_path_plugin/circuit_service_path_include.html",
            extra_context={
                "related_session_table": service_path_table,
            },
        )


class SegmentToCircuit(PluginTemplateExtension):
    model = "circuits.circuit"
    exclude = ()

    def full_width_page(self):
        circuit = self.context["object"]

        segment_ids = SegmentCircuitMapping.objects.filter(
            circuit=circuit.id
        ).values_list("segment_id", flat=True)

        segments = Segment.objects.filter(id__in=segment_ids).all()
        segment_table = SegmentTable(
            segments, exclude=self.exclude
        )

        return self.render(
            "komora_service_path_plugin/circuit_service_path_include.html",
            extra_context={
                "related_session_table": segment_table,
            },
        )


class CircuitToSegment(PluginTemplateExtension):
    # TODO: does not make sense, vytvorim primo v Segment
    pass


class CircuitToServicePath(PluginTemplateExtension):
    # TODO: does not make sense, vytvorim primo v ServicePath
    pass


template_extensions = [
    SegmentMappingListToServicePath,
    SegmentToCircuit,
    ServicePathToCircuit,
]
