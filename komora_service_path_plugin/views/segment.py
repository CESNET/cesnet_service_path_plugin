from django.db.models import Count

from netbox.views import generic
from ..forms import SegmentForm
from ..models import Segment
from ..tables import SegmentTable
from ..filtersets import SegmentFilterSet


class SegmentView(generic.ObjectView):
    queryset = Segment.objects.all()


class SegmentListView(generic.ObjectListView):
    queryset = Segment.objects.all()
    table = SegmentTable


class SegmentEditView(generic.ObjectEditView):
    queryset = Segment.objects.all()
    form = SegmentForm


class SegmentDeleteView(generic.ObjectDeleteView):
    queryset = Segment.objects.all()
