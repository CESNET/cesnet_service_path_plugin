from netbox.filtersets import NetBoxModelFilterSet
from komora_service_path_plugin.models import SegmentCircuitMapping


class SegmentCircuitMappingFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = SegmentCircuitMapping
        fields = [
            "id",
            "segment",
            "circuit",
        ]

    def search(self, queryset, name, value):
        # TODO:
        return queryset
