from django.db.models import Count

from netbox.views import generic
from ..forms import SegmentPathForm
from ..models import SegmentPath
from ..tables import SegmentPathTable
from ..filtersets import SegmentPathFilterSet


class SegmentPathView(generic.ObjectView):
    queryset = SegmentPath.objects.all()


class SegmentPathListView(generic.ObjectListView):
    queryset = SegmentPath.objects.all()
    table = SegmentPathTable


class SegmentPathEditView(generic.ObjectEditView):
    queryset = SegmentPath.objects.all()
    form = SegmentPathForm


class SegmentPathDeleteView(generic.ObjectDeleteView):
    queryset = SegmentPath.objects.all()
