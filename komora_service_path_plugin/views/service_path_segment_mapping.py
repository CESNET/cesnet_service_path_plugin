from django.db.models import Count

from netbox.views import generic

# from ..filtersets import ServicePathSegmentMappingFilterSet
from ..models import ServicePathSegmentMapping
from ..forms import ServicePathSegmentMappingForm
from ..tables import ServicePathSegmentMappingTable


class ServicePathSegmentMappingView(generic.ObjectView):
    queryset = ServicePathSegmentMapping.objects.all()


class ServicePathSegmentMappingListView(generic.ObjectListView):
    queryset = ServicePathSegmentMapping.objects.all()
    table = ServicePathSegmentMappingTable


class ServicePathSegmentMappingEditView(generic.ObjectEditView):
    queryset = ServicePathSegmentMapping.objects.all()
    form = ServicePathSegmentMappingForm


class ServicePathSegmentMappingDeleteView(generic.ObjectDeleteView):
    queryset = ServicePathSegmentMapping.objects.all()
