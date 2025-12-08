from django.utils.http import url_has_allowed_host_and_scheme
from netbox.views import generic
from utilities.views import register_model_view
from netbox.object_actions import CloneObject as BaseCloneObject, EditObject, DeleteObject

from cesnet_service_path_plugin.filtersets import ContractInfoFilterSet
from cesnet_service_path_plugin.forms import ContractInfoForm, ContractInfoFilterForm
from cesnet_service_path_plugin.models import ContractInfo
from cesnet_service_path_plugin.tables import ContractInfoTable


class CloneActiveContractOnly(BaseCloneObject):
    """
    Custom clone action that only allows cloning of active (non-superseded) contract versions.
    This prevents database integrity errors from attempting to clone older versions.
    """
    label = 'New Version'
    template_name = 'buttons/clone_custom.html'

    @classmethod
    def get_url(cls, obj):
        # Only allow cloning if the contract is active (not superseded)
        if not obj.is_active:
            return None
        return super().get_url(obj)


@register_model_view(ContractInfo, "list", path="", detail=False)
class ContractInfoListView(generic.ObjectListView):
    """List view for ContractInfo objects with filtering and search"""

    queryset = ContractInfo.objects.all()
    table = ContractInfoTable
    filterset = ContractInfoFilterSet
    filterset_form = ContractInfoFilterForm


@register_model_view(ContractInfo)
class ContractInfoView(generic.ObjectView):
    """Detail view for ContractInfo with version history and financial summary"""

    queryset = ContractInfo.objects.prefetch_related("segments")
    actions = (CloneActiveContractOnly, EditObject, DeleteObject)

    def get_extra_context(self, request, instance):
        """Add version history and related segments to context"""
        context = super().get_extra_context(request, instance)

        # Get version history
        version_history = instance.get_version_history()

        # Get related segments
        segments = instance.segments.all()

        context.update(
            {
                "version_history": version_history,
                "segments": segments,
                "is_latest_version": instance.is_latest_version(),
                "first_version": instance.get_first_version(),
                "latest_version": instance.get_latest_version(),
            }
        )

        return context


@register_model_view(ContractInfo, "add", detail=False)
@register_model_view(ContractInfo, "edit")
class ContractInfoEditView(generic.ObjectEditView):
    queryset = ContractInfo.objects.all()
    form = ContractInfoForm

    def alter_object(self, obj, request, url_args, url_kwargs):
        """
        Hook to modify the object before saving.
        Handle previous_version from clone URL.
        """
        # Check if previous_version is in the GET/POST parameters (from clone)
        previous_version_ref = request.GET.get("previous_version") or request.POST.get("previous_version")

        if previous_version_ref and not obj.pk:  # Only for new objects
            try:
                # Try to get by ID first
                try:
                    previous_version = ContractInfo.objects.get(pk=int(previous_version_ref))
                except (ValueError, TypeError):
                    # If not an ID, try by contract_number
                    previous_version = ContractInfo.objects.get(contract_number=previous_version_ref)

                # Set the version chain
                obj.previous_version = previous_version

            except ContractInfo.DoesNotExist:
                pass  # If not found, just continue

        return obj

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


@register_model_view(ContractInfo, "delete")
class ContractInfoDeleteView(generic.ObjectDeleteView):
    queryset = ContractInfo.objects.all()

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
