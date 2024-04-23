from netbox.filtersets import NetBoxModelFilterSet
from . import service_path


# class komora_service_path_pluginFilterSet(NetBoxModelFilterSet):
#
#     class Meta:
#         model = komora_service_path_plugin
#         fields = ['name', ]
#
#     def search(self, queryset, name, value):
#         return queryset.filter(description__icontains=value)
