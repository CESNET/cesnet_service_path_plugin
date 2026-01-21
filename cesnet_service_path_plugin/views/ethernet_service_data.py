from django.utils.http import url_has_allowed_host_and_scheme
from netbox.views import generic
from utilities.views import register_model_view

from cesnet_service_path_plugin.forms import EthernetServiceSegmentDataForm
from cesnet_service_path_plugin.models import EthernetServiceSegmentData, Segment


@register_model_view(EthernetServiceSegmentData, "add", detail=False)
@register_model_view(EthernetServiceSegmentData, "edit")
class EthernetServiceSegmentDataEditView(generic.ObjectEditView):
    """
    View for adding/editing ethernet service technical data.

    The segment is expected to be passed via URL parameter (segment_id) for add,
    or derived from the instance for edit operations.
    """
    queryset = EthernetServiceSegmentData.objects.all()
    form = EthernetServiceSegmentDataForm

    def alter_object(self, obj, request, url_args, url_kwargs):
        """
        Set the segment for new objects based on URL parameter.
        """
        if not obj.segment_id:
            # Get segment_id from URL parameter for new objects
            segment_id = request.GET.get('segment')
            if segment_id:
                try:
                    obj.segment = Segment.objects.get(pk=segment_id)
                except Segment.DoesNotExist:
                    pass
        return obj

    def get_return_url(self, request, obj=None):
        """
        Return to the parent segment's detail view after save.
        """
        # Check if return_url is in request
        if return_url := request.GET.get("return_url") or request.POST.get("return_url"):
            # Validate the return_url to prevent open redirect
            if url_has_allowed_host_and_scheme(return_url, allowed_hosts={request.get_host()}, require_https=True):
                return return_url

        # Default: return to segment detail if we have an object
        if obj and obj.segment:
            return obj.segment.get_absolute_url()

        # Fallback to default behavior
        return super().get_return_url(request, obj)


@register_model_view(EthernetServiceSegmentData, "delete")
class EthernetServiceSegmentDataDeleteView(generic.ObjectDeleteView):
    """
    View for deleting ethernet service technical data.
    """
    queryset = EthernetServiceSegmentData.objects.all()

    def get(self, request, *args, **kwargs):
        """Store the segment reference before the object might be deleted."""
        obj = self.get_object(**kwargs)
        try:
            self._segment_url = obj.segment.get_absolute_url() if obj.segment else None
        except Exception:
            self._segment_url = None
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Store the segment reference before the object is deleted."""
        obj = self.get_object(**kwargs)
        try:
            self._segment_url = obj.segment.get_absolute_url() if obj.segment else None
        except Exception:
            self._segment_url = None
        return super().post(request, *args, **kwargs)

    def get_return_url(self, request, obj=None):
        """
        Return to the parent segment's detail view after delete.
        """
        # Check if return_url is in request
        if return_url := request.GET.get("return_url") or request.POST.get("return_url"):
            # Validate the return_url to prevent open redirect
            if url_has_allowed_host_and_scheme(return_url, allowed_hosts={request.get_host()}, require_https=True):
                return return_url

        # Use the stored segment URL if available
        if hasattr(self, '_segment_url') and self._segment_url:
            return self._segment_url

        # Fallback to default behavior
        return super().get_return_url(request, obj)
