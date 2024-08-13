from netbox.views import generic

from komora_service_path_plugin.filtersets import ServicePathFilterSet
from komora_service_path_plugin.forms import ServicePathFilterForm, ServicePathForm
from komora_service_path_plugin.models import ServicePath
from komora_service_path_plugin.tables import ServicePathTable


class ServicePathView(generic.ObjectView):
    queryset = ServicePath.objects.all()


class ServicePathListView(generic.ObjectListView):
    queryset = ServicePath.objects.all()
    table = ServicePathTable

    actions = {
        "add": {},
        "edit": {"add"},
        "import": {},
        "export": set(),
        "bulk_edit": {},
        "bulk_delete": {},
    }

    filterset = ServicePathFilterSet
    filterset_form = ServicePathFilterForm


class ServicePathEditView(generic.ObjectEditView):
    queryset = ServicePath.objects.all()
    form = ServicePathForm
