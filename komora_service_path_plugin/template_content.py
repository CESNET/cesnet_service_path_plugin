from django.conf import settings
from django.db.models import F

from dcim.models import Device, Interface
from ipam.models import IPAddress, Prefix, VRF
from tenancy.models import Tenant

from extras.plugins import PluginTemplateExtension
from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from komora_service_path_plugin.filtersets import (
    SegmentFilterSet,
    ServicePathFilterSet,
    ServicePathSegmentMappingFilterSet,
)
from komora_service_path_plugin.models import (
    Segment,
    ServicePath,
    ServicePathSegmentMapping,
)
from komora_service_path_plugin.tables import (
    SegmentTable,
    ServicePathSegmentMappingTable,
    ServicePathTable,
)


plugin_settings = settings.PLUGINS_CONFIG.get("komora_service_path_plugin", {})


class SegmentMappingList(PluginTemplateExtension):
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
    SegmentMappingList,
]
