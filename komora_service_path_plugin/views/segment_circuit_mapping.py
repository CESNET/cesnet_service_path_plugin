from django.db.models import Count

from netbox.views import generic

# from ..filtersets import SegmentCircuitMappingFilterSet
from komora_service_path_plugin.models import SegmentCircuitMapping
from komora_service_path_plugin.forms import SegmentCircuitMappingForm
from komora_service_path_plugin.tables import SegmentCircuitMappingTable


class SegmentCircuitMappingView(generic.ObjectView):
    queryset = SegmentCircuitMapping.objects.all()


class SegmentCircuitMappingListView(generic.ObjectListView):
    queryset = SegmentCircuitMapping.objects.all()
    table = SegmentCircuitMappingTable


class SegmentCircuitMappingEditView(generic.ObjectEditView):
    queryset = SegmentCircuitMapping.objects.all()
    form = SegmentCircuitMappingForm


class SegmentCircuitMappingDeleteView(generic.ObjectDeleteView):
    queryset = SegmentCircuitMapping.objects.all()
