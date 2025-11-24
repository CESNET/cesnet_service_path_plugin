from django import forms
from netbox.forms import NetBoxModelForm
from utilities.forms.fields import DynamicModelMultipleChoiceField
from utilities.forms.rendering import FieldSet

from cesnet_service_path_plugin.models import Segment, ContractInfo
from cesnet_service_path_plugin.models.custom_choices import (
    CurrencyChoices,
    RecurringChargePeriodChoices,
)


class ContractInfoForm(NetBoxModelForm):
    segments = DynamicModelMultipleChoiceField(
        queryset=Segment.objects.all(),
        required=False,
        help_text="Network segments covered by this contract",
    )

    contract_number = forms.CharField(max_length=100, required=False, help_text="Provider's contract reference number")

    effective_date = forms.DateField(required=True, help_text="When this contract version becomes effective")

    change_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        help_text="Reason for creating this version (required for amendments/renewals)",
    )

    charge_currency = forms.ChoiceField(
        required=True, choices=CurrencyChoices, help_text="Currency for all charges (cannot be changed in amendments)"
    )

    non_recurring_charge = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        help_text="One-time fees for this version (setup, installation, etc.)",
    )

    cumulative_notes = forms.CharField(
        required=False,
        disabled=True,
        widget=forms.Textarea(attrs={"rows": 5, "readonly": "readonly"}),
        help_text="Accumulated notes across all versions (read-only, automatically generated)",
    )

    recurring_charge = forms.DecimalField(
        max_digits=10, decimal_places=2, required=True, help_text="Recurring fee amount"
    )

    recurring_charge_period = forms.ChoiceField(
        required=True, choices=RecurringChargePeriodChoices, help_text="Frequency of recurring charges"
    )

    number_of_recurring_charges = forms.IntegerField(
        required=True, min_value=1, help_text="Number of recurring charge periods in this contract"
    )

    start_date = forms.DateField(required=True, help_text="When this contract version starts")

    end_date = forms.DateField(required=False, help_text="When this contract version ends (optional)")

    commitment_end_date = forms.DateField(
        required=False, help_text="End of commitment period (defaults to end_date if not specified)"
    )

    notes = forms.CharField(
        required=False, widget=forms.Textarea(attrs={"rows": 3}), help_text="Notes specific to this version"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = ContractInfo
        fields = [
            "segments",
            "contract_number",
            "effective_date",
            "change_reason",
            "charge_currency",
            "non_recurring_charge",
            "cumulative_notes",
            "recurring_charge",
            "recurring_charge_period",
            "number_of_recurring_charges",
            "start_date",
            "end_date",
            "commitment_end_date",
            "notes",
        ]

    fieldsets = (
        FieldSet(
            "segments",
            name="Segments",
        ),
        FieldSet(
            "contract_number",
            "effective_date",
            "change_reason",
            name="Contract Metadata",
        ),
        FieldSet(
            "charge_currency",
            "recurring_charge",
            "recurring_charge_period",
            "number_of_recurring_charges",
            "non_recurring_charge",
            name="Charges",
        ),
        FieldSet(
            "start_date",
            "end_date",
            "commitment_end_date",
            name="Dates",
        ),
        FieldSet(
            "notes",
            "cumulative_notes",
            name="Notes",
        ),
    )
