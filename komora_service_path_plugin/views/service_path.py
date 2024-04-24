from django.db.models import Count

from netbox.views import generic
from ..filtersets import ServicePathFilterSet
from ..forms import ServicePathForm
from ..models import ServicePath
from ..tables import ServicePathTable


class ServicePathView(generic.ObjectView):
    queryset = ServicePath.objects.all()


class ServicePathListView(generic.ObjectListView):
    queryset = ServicePath.objects.all()
    table = ServicePathTable


class ServicePathEditView(generic.ObjectEditView):
    queryset = ServicePath.objects.all()
    form = ServicePathForm


class ServicePathDeleteView(generic.ObjectDeleteView):
    queryset = ServicePath.objects.all()
