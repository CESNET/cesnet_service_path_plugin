from django.shortcuts import redirect
from netbox.views import generic
from utilities.views import register_model_view

from cesnet_service_path_plugin.forms import SegmentFinancialInfoForm
from cesnet_service_path_plugin.models import SegmentFinancialInfo


@register_model_view(SegmentFinancialInfo)
class SegmentFinancialInfoView(generic.ObjectView):
    """
    Redirect to the parent segment's detail view instead of showing a separate detail page
    """

    queryset = SegmentFinancialInfo.objects.all()

    def get(self, request, *args, **kwargs):
        obj = self.get_object(**kwargs)
        # Redirect to the parent segment's detail view
        return redirect(obj.segment.get_absolute_url())


@register_model_view(SegmentFinancialInfo, "add", detail=False)
@register_model_view(SegmentFinancialInfo, "edit")
class SegmentFinancialInfoEditView(generic.ObjectEditView):
    queryset = SegmentFinancialInfo.objects.all()
    form = SegmentFinancialInfoForm

    def get_return_url(self, request, obj=None):
        """
        Return to the parent segment's detail view after save
        """
        # Check if return_url is in request
        if return_url := request.GET.get("return_url") or request.POST.get("return_url"):
            return return_url

        # Otherwise return to the segment detail
        if obj and obj.segment:
            return obj.segment.get_absolute_url()

        # Fallback to the default behavior
        return super().get_return_url(request, obj)


@register_model_view(SegmentFinancialInfo, "delete")
class SegmentFinancialInfoDeleteView(generic.ObjectDeleteView):
    queryset = SegmentFinancialInfo.objects.all()

    def get_return_url(self, request, obj=None):
        """
        Return to the parent segment's detail view after delete
        """
        # Check if return_url is in request
        if return_url := request.GET.get("return_url") or request.POST.get("return_url"):
            return return_url

        # Otherwise return to the segment detail
        if obj and obj.segment:
            return obj.segment.get_absolute_url()

        # Fallback to the default behavior
        return super().get_return_url(request, obj)
