from netbox.api.viewsets import NetBoxModelViewSet

from cesnet_service_path_plugin.models import ContractInfo
from cesnet_service_path_plugin.api.serializers import ContractInfoSerializer


class ContractInfoViewSet(NetBoxModelViewSet):
    queryset = ContractInfo.objects.all()
    serializer_class = ContractInfoSerializer
