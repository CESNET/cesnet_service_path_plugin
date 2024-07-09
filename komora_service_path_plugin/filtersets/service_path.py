from netbox.filtersets import NetBoxModelFilterSet
from ..models import ServicePath


class ServicePathFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = ServicePath
        fields = ["id", "name", "komora_id"]

    def search(self, queryset, name, value):
        # TODO:
        return queryset.filter(name__icontains=value)
