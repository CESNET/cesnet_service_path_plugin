from netbox.views import generic

from cesnet_service_path_plugin.filtersets import ServicePathFilterSet
from cesnet_service_path_plugin.forms import ServicePathFilterForm, ServicePathForm
from cesnet_service_path_plugin.models import ServicePath
from cesnet_service_path_plugin.tables import ServicePathTable


class ServicePathView(generic.ObjectView):
    queryset = ServicePath.objects.all()


class ServicePathListView(generic.ObjectListView):
    queryset = ServicePath.objects.all()
    table = ServicePathTable
    filterset = ServicePathFilterSet
    filterset_form = ServicePathFilterForm


class ServicePathEditView(generic.ObjectEditView):
    queryset = ServicePath.objects.all()
    form = ServicePathForm


class ServicePathDeleteView(generic.ObjectDeleteView):
    queryset = ServicePath.objects.all()
