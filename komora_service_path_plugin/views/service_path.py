from django.db.models import Count

from netbox.views import generic
from . import filtersets, forms, models, tables


class ServicePathView(generic.ObjectView):
    queryset = models.ServicePath.objects.all()


class ServicePathListView(generic.ObjectListView):
    queryset = models.ServicePath.objects.all()
    table = tables.ServicePathTable


class ServicePathEditView(generic.ObjectEditView):
    queryset = models.ServicePath.objects.all()
    form = forms.ServicePathForm


class ServicePathDeleteView(generic.ObjectDeleteView):
    queryset = models.ServicePath.objects.all()
