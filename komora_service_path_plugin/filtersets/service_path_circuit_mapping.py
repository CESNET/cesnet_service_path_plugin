from netbox.filtersets import NetBoxModelFilterSet
from komora_service_path_plugin.models import ServicePathCircuitMapping


class ServicePathCircuitMappingFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = ServicePathCircuitMapping
        fields = [
            "id",
            "service_path",
            "circuit",
        ]

    def search(self, queryset, name, value):
        # TODO:
        return queryset
