from django.db.models import Count

from netbox.views import generic

# from ..filtersets import ServicePathFilterSet
from komora_service_path_plugin.forms import ServicePathForm
from komora_service_path_plugin.models import ServicePath
from komora_service_path_plugin.tables import ServicePathTable
from circuits.tables import CircuitTable


class ServicePathView(generic.ObjectView):
    queryset = ServicePath.objects.all()

    def get_extra_context(self, request, instance):
        circuits = instance.circuits.all()
        circuits_table = CircuitTable(circuits, exclude=())
        return {"circuits_table": circuits_table}


class ServicePathListView(generic.ObjectListView):
    queryset = ServicePath.objects.all()
    table = ServicePathTable


class ServicePathEditView(generic.ObjectEditView):
    queryset = ServicePath.objects.all()
    form = ServicePathForm


class ServicePathDeleteView(generic.ObjectDeleteView):
    queryset = ServicePath.objects.all()
