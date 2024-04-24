from netbox.filtersets import NetBoxModelFilterSet
from ..models import SegmentPath


class SegmentPathFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = SegmentPath
        fields = []

    def search(self, queryset, name, value):
        return queryset.filter(description__icontains=value)
