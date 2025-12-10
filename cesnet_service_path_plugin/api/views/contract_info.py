from netbox.api.viewsets import NetBoxModelViewSet

from cesnet_service_path_plugin.models import ContractInfo
from cesnet_service_path_plugin.api.serializers import ContractInfoSerializer
from cesnet_service_path_plugin.filtersets import ContractInfoFilterSet


class ContractInfoViewSet(NetBoxModelViewSet):
    queryset = ContractInfo.objects.all()
    serializer_class = ContractInfoSerializer
    filterset_class = ContractInfoFilterSet
