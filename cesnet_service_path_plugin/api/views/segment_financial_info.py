# cesnet_service_path_plugin/api/views/segment_financial_info.py
from netbox.api.viewsets import NetBoxModelViewSet

from cesnet_service_path_plugin.models import SegmentFinancialInfo
from cesnet_service_path_plugin.api.serializers import SegmentFinancialInfoSerializer


class SegmentFinancialInfoViewSet(NetBoxModelViewSet):
    queryset = SegmentFinancialInfo.objects.all()
    serializer_class = SegmentFinancialInfoSerializer
