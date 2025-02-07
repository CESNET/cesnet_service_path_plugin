from circuits.models import Circuit, Provider
from dcim.models import Device, Interface, Location, Site
from django import forms
from django.utils.translation import gettext as _
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms.fields import (
    CommentField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets.datetime import DatePicker

from cesnet_service_path_plugin.models import Segment, SyncStatusChoices


class SegmentForm(NetBoxModelForm):
    comments = CommentField(required=False, label="Comments", help_text="Comments")

    class Meta:
        model = Segment
        fields = [
            "name",
            "network_label",
            "install_date",
            "termination_date",
            "provider",
            "provider_segment_id",
            "provider_segment_name",
            "provider_segment_contract",
            "site_a",
            "location_a",
            "site_b",
            "location_b",
            "tags",
            "comments",
        ]


class SegmentFilterForm(NetBoxModelFilterSetForm):
    model = Segment

    name = forms.CharField(required=False)
    sync_status = forms.MultipleChoiceField(
        required=False,
        choices=SyncStatusChoices,
    )
    network_label = forms.CharField(required=False)

    tag = TagFilterField(model)

    site_a_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(), required=False, label=_("Site A")
    )
    location_a_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            "site_id": "$site_a_id",
        },
        label=_("Location A"),
    )

    site_b_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(), required=False, label=_("Site B")
    )
    location_b_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            "site_id": "$site_b_id",
        },
        label=_("Location B"),
    )

    install_date__gte = forms.DateTimeField(
        required=False, label=("Install Date From"), widget=DatePicker()
    )
    install_date__lte = forms.DateTimeField(
        required=False, label=("Install Date Till"), widget=DatePicker()
    )
    termination_date__gte = forms.DateTimeField(
        required=False, label=("Termination Date From"), widget=DatePicker()
    )
    termination_date__lte = forms.DateTimeField(
        required=False, label=("Termination Date Till"), widget=DatePicker()
    )

    provider_id = DynamicModelMultipleChoiceField(
        queryset=Provider.objects.all(), required=False, label=_("Provider")
    )
    provider_segment_id = forms.CharField(
        required=False, label=_("Provider Segment ID")
    )
    provider_segment_name = forms.CharField(
        required=False, label=_("Provider Segment Name")
    )
    provider_segment_contract = forms.CharField(
        required=False, label=_("Provider Segment Contract")
    )

    at_any_site = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label=_("At any Site"),
    )

    at_any_location = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        label=_("At any Location"),
    )

    circuits = DynamicModelMultipleChoiceField(
        queryset=Circuit.objects.all(),
        required=False,
        label=_("Circuits"),
    )

    fieldsets = (
        FieldSet("q", "tag", "filter_id", "sync_status", name="Misc"),
        FieldSet("name", "network_label", name="Basic"),
        FieldSet(
            "provider_id",
            "provider_segment_id",
            "provider_segment_name",
            "provider_segment_contract",
            name="Provider",
        ),
        FieldSet(
            "install_date__gte",
            "install_date__lte",
            "termination_date__gte",
            "termination_date__lte",
            name="Dates",
        ),
        FieldSet("circuits", "at_any_site", "at_any_location", name="Extra"),
        FieldSet("site_a_id", "location_a_id", name="Side A"),
        FieldSet("site_b_id", "location_b_id", name="Side B"),
    )
