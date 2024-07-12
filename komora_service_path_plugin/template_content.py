from django.conf import settings
from circuits.models import Circuit
from komora_service_path_plugin.filtersets import SegmentFilterSet
from netbox.plugins import PluginTemplateExtension
from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from komora_service_path_plugin.models import (
    SegmentCircuitMapping,
    Segment,
)
from komora_service_path_plugin.tables import (
    SegmentTable,
)

plugin_settings = settings.PLUGINS_CONFIG.get("komora_service_path_plugin", {})


# class SegmentMappingListToServicePath(PluginTemplateExtension):
#    model = "komora_service_path_plugin.servicepath"
#    exclude = ("service_path", "id")
#
#
#    def full_width_page(self):
#        service_path = self.context["object"]
#        segment_mapping = ServicePathSegmentMapping.objects.filter(
#            service_path=service_path.id
#        ).order_by("index")
#        segment_mapping_table = ServicePathSegmentMappingTable(
#            segment_mapping, exclude=self.exclude
#        )
#
#        return self.render(
#            "komora_service_path_plugin/segment_mapping_include.html",
#            extra_context={
#                "segment_mapping": segment_mapping,
#                "related_session_table": segment_mapping_table,
#            },
#        )
#
#
# template_extensions = [
#    SegmentMappingListToServicePath,
# ]


@register_model_view(Circuit, name='circuit-komora-segment', path='circuit-komora-segment')
class CircuitKomoraSegmentView(generic.ObjectChildrenView):
    queryset = Circuit.objects.all()
    child_model = Segment
    table = SegmentTable
    filterset = SegmentFilterSet

    template_name = "komora_service_path_plugin/circuit_komora_segments_tab.html"
    tab = ViewTab(
        label='Segments',
        badge=lambda obj: SegmentCircuitMapping.objects.filter(
            circuit=obj.id).count(),
        # permission='myplugin.view_stuff'
    )

    def get_children(self, request, instance):
        segment_mapping = SegmentCircuitMapping.objects.filter(
            circuit=instance.id).values_list('segment_id', flat=True)
        childrens = Segment.objects.filter(id__in=segment_mapping)
        return childrens

    def get_extra_context(self, request, instance):
        data = {
            "base_template_name": "generic/object.html",
        }
        return data
