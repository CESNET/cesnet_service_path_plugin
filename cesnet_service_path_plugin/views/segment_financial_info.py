from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
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
        # Check if segment exists before redirecting
        if obj.segment is None:
            return redirect("/")
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
            # Validate the return_url to prevent open redirect
            if url_has_allowed_host_and_scheme(return_url, allowed_hosts={request.get_host()}, require_https=True):
                return return_url

        # Return safe default if validation fails or no return_url provided
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
            # Validate the return_url to prevent open redirect
            if url_has_allowed_host_and_scheme(return_url, allowed_hosts={request.get_host()}, require_https=True):
                return return_url

        # Return safe default if validation fails or no return_url provided
        return super().get_return_url(request, obj)
