from django.db.models import Count

from netbox.views import generic
from . import filtersets, forms, models, tables


class SegmentPathView(generic.ObjectView):
    queryset = models.SegmentPath.objects.all()


class SegmentPathListView(generic.ObjectListView):
    queryset = models.SegmentPath.objects.all()
    table = tables.SegmentPathTable


class SegmentPathEditView(generic.ObjectEditView):
    queryset = models.SegmentPath.objects.all()
    form = forms.SegmentPathForm


class SegmentPathDeleteView(generic.ObjectDeleteView):
    queryset = models.SegmentPath.objects.all()
