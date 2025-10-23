from netbox.views import generic
from utilities.views import register_model_view

from cesnet_service_path_plugin.filtersets import SegmentCircuitMappingFilterSet
from cesnet_service_path_plugin.forms import (
    SegmentCircuitMappingBulkEditForm,
    SegmentCircuitMappingForm,
)
from cesnet_service_path_plugin.models import SegmentCircuitMapping
from cesnet_service_path_plugin.tables import SegmentCircuitMappingTable


@register_model_view(SegmentCircuitMapping, "list", path="", detail=False)
class SegmentCircuitMappingListView(generic.ObjectListView):
    queryset = SegmentCircuitMapping.objects.all()
    table = SegmentCircuitMappingTable
    filterset = SegmentCircuitMappingFilterSet


# From Circuit to Segment
# Create/Edit View
@register_model_view(SegmentCircuitMapping, "add", detail=False)
@register_model_view(SegmentCircuitMapping, "edit")
class SegmentCircuitMappingEditView(generic.ObjectEditView):
    queryset = SegmentCircuitMapping.objects.all()
    form = SegmentCircuitMappingForm


@register_model_view(SegmentCircuitMapping, "delete")
class SegmentCircuitMappingDeleteView(generic.ObjectDeleteView):
    queryset = SegmentCircuitMapping.objects.all()


@register_model_view(SegmentCircuitMapping)
class SegmentCircuitMappingView(generic.ObjectView):
    queryset = SegmentCircuitMapping.objects.all()
    template_name = "cesnet_service_path_plugin/segmentcircuitmapping.html"


@register_model_view(SegmentCircuitMapping, "bulk_edit", path="edit", detail=False)
class SegmentCircuitMappingBulkEditView(generic.BulkEditView):
    queryset = SegmentCircuitMapping.objects.all()
    filterset = SegmentCircuitMappingFilterSet
    table = SegmentCircuitMappingTable
    form = SegmentCircuitMappingBulkEditForm


@register_model_view(SegmentCircuitMapping, "bulk_delete", path="delete", detail=False)
class SegmentCircuitMappingBulkDeleteView(generic.BulkDeleteView):
    queryset = SegmentCircuitMapping.objects.all()
    filterset = SegmentCircuitMappingFilterSet
    table = SegmentCircuitMappingTable


@register_model_view(SegmentCircuitMapping, "bulk_import", path="import", detail=False)
class SegmentCircuitMappingBulkImportView(generic.BulkImportView):
    queryset = SegmentCircuitMapping.objects.all()
    model_form = SegmentCircuitMappingForm
    table = SegmentCircuitMappingTable
