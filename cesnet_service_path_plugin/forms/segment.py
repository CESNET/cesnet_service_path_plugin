from circuits.models import Circuit, Provider
from dcim.models import Location, Site
from django import forms
from django.utils.translation import gettext as _
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms.fields import (
    CommentField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet, InlineFields
from utilities.forms.widgets.datetime import DatePicker

from cesnet_service_path_plugin.models import Segment
from cesnet_service_path_plugin.models.custom_choices import StatusChoices


class SegmentForm(NetBoxModelForm):
    comments = CommentField(required=False, label="Comments", help_text="Comments")
    status = forms.ChoiceField(required=True, choices=StatusChoices, initial=None)
    provider_segment_contract = forms.CharField(
        label=" Contract", required=False, help_text="Provider Segment Contract"
    )
    provider_segment_id = forms.CharField(
        label=" ID", required=False, help_text="Provider Segment ID"
    )
    provider_segment_name = forms.CharField(
        label="Name", required=False, help_text="Provider Segment Name"
    )
    provider = DynamicModelChoiceField(
        queryset=Provider.objects.all(),
        required=True,
        label=_("Provider"),
        selector=True,
    )
    install_date = forms.DateField(widget=DatePicker(), required=False)
    termination_date = forms.DateField(widget=DatePicker(), required=False)

    site_a = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        label=_("Site A"),
        selector=True,
    )
    location_a = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        query_params={
            "site_id": "$site_a",
        },
        label=_("Location A"),
    )
    site_b = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        label=_("Site B"),
        selector=True,
    )
    location_b = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        query_params={
            "site_id": "$site_b",
        },
        label=_("Location B"),
    )

    def _validate_dates(self, install_date, termination_date):
        """
        WARN: Workaround InlineFields does not display ValidationError messages in the field.
        It has to be raise as popup.

        Validate that install_date is not later than termination_date.
        """
        if install_date and termination_date:
            if install_date > termination_date:
                self.add_error(
                    field=None,  # 'install_date', 'termination_date', # CANNOT BE DEFINED
                    error=[
                        _("Install date cannot be later than termination date."),
                        _("Termination date cannot be earlier than install date."),
                    ],
                )

    def clean(self):
        super().clean()

        install_date = self.cleaned_data.get("install_date")
        termination_date = self.cleaned_data.get("termination_date")

        self._validate_dates(install_date, termination_date)

        return self.cleaned_data

    class Meta:
        model = Segment
        fields = [
            "name",
            "status",
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

    fieldsets = (
        FieldSet(
            "name",
            "network_label",
            "status",
            InlineFields("install_date", "termination_date", label="Dates"),
            name="Basic Information",
        ),
        FieldSet(
            "provider",
            "provider_segment_id",
            "provider_segment_name",
            "provider_segment_contract",
            name="Provider",
        ),
        # FieldSet(
        #   # NOTE: WARNING: InlineFields does not display REQUIRED asterisk (*) in the form!!
        #   InlineFields("site_a", "location_a", label="Side A"),
        #   InlineFields("site_b", "location_b", label="Side B"),
        #   name="Endpoints",
        # ),
        FieldSet(
            "site_a",
            "location_a",
            name="Side A",
        ),
        FieldSet(
            "site_b",
            "location_b",
            name="Side B",
        ),
        FieldSet(
            "tags",
            # "comments", # Comment Is always rendered! If uncommented, it will be rendered twice
            name="Miscellaneous",
        ),
    )


class SegmentFilterForm(NetBoxModelFilterSetForm):
    model = Segment

    name = forms.CharField(required=False)
    status = forms.MultipleChoiceField(
        required=False, choices=StatusChoices, initial=None
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
        FieldSet("q", "tag", "filter_id", name="Misc"),
        FieldSet("name", "status", "network_label", name="Basic"),
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
