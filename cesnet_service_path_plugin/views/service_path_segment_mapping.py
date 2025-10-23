from netbox.views import generic
from utilities.views import register_model_view

from cesnet_service_path_plugin.filtersets import ServicePathSegmentMappingFilterSet
from cesnet_service_path_plugin.forms import (
    ServicePathSegmentMappingBulkEditForm,
    ServicePathSegmentMappingFilterForm,
    ServicePathSegmentMappingForm,
)
from cesnet_service_path_plugin.models import ServicePathSegmentMapping
from cesnet_service_path_plugin.tables import ServicePathSegmentMappingTable


# List View
@register_model_view(ServicePathSegmentMapping, "list", path="", detail=False)
class ServicePathSegmentMappingListView(generic.ObjectListView):
    queryset = ServicePathSegmentMapping.objects.all()
    table = ServicePathSegmentMappingTable
    filterset = ServicePathSegmentMappingFilterSet
    filterset_form = ServicePathSegmentMappingFilterForm


# Detail View
@register_model_view(ServicePathSegmentMapping)
class ServicePathSegmentMappingView(generic.ObjectView):
    queryset = ServicePathSegmentMapping.objects.all()
    template_name = "cesnet_service_path_plugin/servicepathsegmentmapping.html"


# Create/Edit View
@register_model_view(ServicePathSegmentMapping, "add", detail=False)
@register_model_view(ServicePathSegmentMapping, "edit")
class ServicePathSegmentMappingEditView(generic.ObjectEditView):
    queryset = ServicePathSegmentMapping.objects.all()
    form = ServicePathSegmentMappingForm
    # template_name = 'cesnet_service_path_plugin/servicepathsegmentmapping_edit.html'


# Delete View
@register_model_view(ServicePathSegmentMapping, "delete")
class ServicePathSegmentMappingDeleteView(generic.ObjectDeleteView):
    queryset = ServicePathSegmentMapping.objects.all()
    # template_name = 'cesnet_service_path_plugin/servicepathsegmentmapping_delete.html'


@register_model_view(ServicePathSegmentMapping, "bulk_edit", path="edit", detail=False)
class ServicePathSegmentMappingBulkEditView(generic.BulkEditView):
    queryset = ServicePathSegmentMapping.objects.all()
    filterset = ServicePathSegmentMappingFilterSet
    table = ServicePathSegmentMappingTable
    form = ServicePathSegmentMappingBulkEditForm


@register_model_view(ServicePathSegmentMapping, "bulk_delete", path="delete", detail=False)
class ServicePathSegmentMappingBulkDeleteView(generic.BulkDeleteView):
    queryset = ServicePathSegmentMapping.objects.all()
    filterset = ServicePathSegmentMappingFilterSet
    table = ServicePathSegmentMappingTable


@register_model_view(ServicePathSegmentMapping, "bulk_import", path="import", detail=False)
class ServicePathSegmentMappingBulkImportView(generic.BulkImportView):
    queryset = ServicePathSegmentMapping.objects.all()
    model_form = ServicePathSegmentMappingForm
    table = ServicePathSegmentMappingTable
