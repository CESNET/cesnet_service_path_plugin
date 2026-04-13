from circuits.models import CircuitType, Provider
from dcim.choices import SiteStatusChoices
from dcim.models import Region, Site, SiteGroup
from django import forms
from tenancy.models import Tenant
from utilities.forms.fields import DynamicModelMultipleChoiceField

from cesnet_service_path_plugin.models.custom_choices import StatusChoices
from cesnet_service_path_plugin.models.segment_types import SegmentTypeChoices


class MapFilterForm(forms.Form):
    """
    Filter form for the combined Network Map view (Sites + Segments).
    Uses plain forms.Form — no model binding — so DynamicModelMultipleChoiceField
    widgets work independently for each field without SavedFilter/CustomField overhead.

    Field naming convention:
    - Shared spatial fields: native filterset names (region_id, site_group_id, at_any_site)
    - Site-specific fields: site_ prefix (site_status, site_tenant_id)
    - Segment-specific fields: segment_ prefix (segment_status, segment_type, segment_provider_id)

    The view's _extract_*_params() helpers strip/remap these prefixes before
    passing GET params to each filterset.
    """

    # -------------------------------------------------------------------------
    # Shared spatial filters — applied to both Sites and Segments
    # -------------------------------------------------------------------------
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label="Region",
    )
    site_group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label="Site Group",
    )
    at_any_site = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label="Site",
    )

    # -------------------------------------------------------------------------
    # Site filters
    # -------------------------------------------------------------------------
    site_status = forms.MultipleChoiceField(
        choices=SiteStatusChoices,
        required=False,
        label="Status",
        widget=forms.CheckboxSelectMultiple(),
    )
    site_tenant_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label="Tenant",
    )

    # -------------------------------------------------------------------------
    # Segment filters
    # -------------------------------------------------------------------------
    segment_status = forms.MultipleChoiceField(
        choices=StatusChoices,
        required=False,
        label="Status",
        widget=forms.CheckboxSelectMultiple(),
    )
    segment_type = forms.MultipleChoiceField(
        choices=SegmentTypeChoices,
        required=False,
        label="Type",
        widget=forms.CheckboxSelectMultiple(),
    )
    segment_provider_id = DynamicModelMultipleChoiceField(
        queryset=Provider.objects.all(),
        required=False,
        label="Provider",
    )

    # -------------------------------------------------------------------------
    # Circuit filters
    # -------------------------------------------------------------------------
    circuit_status = forms.MultipleChoiceField(
        choices=[],          # populated in __init__ to avoid import-time issues
        required=False,
        label="Status",
        widget=forms.CheckboxSelectMultiple(),
    )
    circuit_type_id = DynamicModelMultipleChoiceField(
        queryset=CircuitType.objects.all(),
        required=False,
        label="Type",
    )
    circuit_provider_id = DynamicModelMultipleChoiceField(
        queryset=Provider.objects.all(),
        required=False,
        label="Provider",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from circuits.choices import CircuitStatusChoices
        self.fields["circuit_status"].choices = list(CircuitStatusChoices)
