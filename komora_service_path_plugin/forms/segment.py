from circuits.models import Provider
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

from komora_service_path_plugin.models import Segment


class SegmentForm(NetBoxModelForm):
    comments = CommentField(required=False, label="Comments", help_text="Comments")

    fieldsets = (
        (
            "Misc",
            (
                "role",
                "tags",
            ),
        ),
    )

    class Meta:
        model = Segment
        fields = (
            "comments",
            "tags",
        )


class SegmentFilterForm(NetBoxModelFilterSetForm):
    model = Segment

    name = forms.CharField(required=False)
    network_label = forms.CharField(required=False)
    komora_id = forms.IntegerField(required=False, label=_("Komora ID"))

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
    device_a_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(), required=False, label=_("Device A")
    )
    port_a_id = DynamicModelMultipleChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        query_params={
            "device_id": "$device_a_id",
        },
        label=_("Port A"),
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
    device_b_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(), required=False, label=_("Device B")
    )
    port_b_id = DynamicModelMultipleChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        query_params={
            "device_id": "$device_b_id",
        },
        label=_("Port B"),
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

    fieldsets = (
        FieldSet("q", "tag", "filter_id", name="Misc"),
        FieldSet("name", "network_label", "komora_id", name="Basic"),
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
        FieldSet(
            "site_a_id", "location_a_id", "device_a_id", "port_a_id", name="Side A"
        ),
        FieldSet(
            "site_b_id", "location_b_id", "device_b_id", "port_b_id", name="Side B"
        ),
    )
