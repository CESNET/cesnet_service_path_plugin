from netbox.views import generic

from cesnet_service_path_plugin.forms import SegmentFinancialInfoForm
from cesnet_service_path_plugin.models import SegmentFinancialInfo


class SegmentFinancialInfoView(generic.ObjectView):
    queryset = SegmentFinancialInfo.objects.all()


class SegmentFinancialInfoEditView(generic.ObjectEditView):
    queryset = SegmentFinancialInfo.objects.all()
    form = SegmentFinancialInfoForm


class SegmentFinancialInfoDeleteView(generic.ObjectDeleteView):
    queryset = SegmentFinancialInfo.objects.all()
