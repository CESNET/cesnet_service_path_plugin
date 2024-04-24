from netbox.filtersets import NetBoxModelFilterSet
from ..models import Segment


class SegmentFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = Segment
        fields = []

    def search(self, queryset, name, value):
        return queryset.filter(description__icontains=value)
