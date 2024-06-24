from django.db.models import Count

from netbox.views import generic
from komora_service_path_plugin.forms import SegmentForm
from komora_service_path_plugin.models import Segment
from komora_service_path_plugin.tables import SegmentTable
# from ..filtersets import SegmentFilterSet
from circuits.tables import CircuitTable


class SegmentView(generic.ObjectView):
    queryset = Segment.objects.all()

    def get_extra_context(self, request, instance):
        circuits = instance.circuits.all()
        circuits_table = CircuitTable(circuits, exclude=())
        return {"circuits_table": circuits_table}


class SegmentListView(generic.ObjectListView):
    queryset = Segment.objects.all()
    table = SegmentTable


class SegmentEditView(generic.ObjectEditView):
    queryset = Segment.objects.all()
    form = SegmentForm


class SegmentDeleteView(generic.ObjectDeleteView):
    queryset = Segment.objects.all()
