from netbox.filtersets import NetBoxModelFilterSet
from ..models import ServicePath


class ServicePathFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = ServicePath
        fields = []

    def search(self, queryset, name, value):
        return queryset.filter(description__icontains=value)
