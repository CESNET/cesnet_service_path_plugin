from netbox.filtersets import NetBoxModelFilterSet
from ..models import ServicePathSegmentMapping


class ServicePathSegmentMappingFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = ServicePathSegmentMapping
        fields = [
            "service_path",
            "segment",
            "index",
        ]

    def search(self, queryset, name, value):
        # TODO:
        return queryset
