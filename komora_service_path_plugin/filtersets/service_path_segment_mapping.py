from netbox.filtersets import NetBoxModelFilterSet
from ..models import ServicePathSegmentMapping


class ServicePathSegmentMappingFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = ServicePathSegmentMapping
        fields = [
            "id",
            "service_path",
            "segment",
            "index",
            "komora_id",
        ]

    def search(self, queryset, name, value):
        # TODO:
        return queryset
