from django import forms
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import DynamicModelMultipleChoiceField, TagFilterField
from utilities.forms.rendering import FieldSet

from cesnet_service_path_plugin.models import Segment, ContractInfo
from cesnet_service_path_plugin.models.custom_choices import (
    ContractTypeChoices,
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
        max_digits=10, decimal_places=2, required=False, help_text="Recurring fee amount (required for new contracts)"
    )

    recurring_charge_period = forms.ChoiceField(
        required=False, choices=RecurringChargePeriodChoices, help_text="Frequency of recurring charges"
    )

    number_of_recurring_charges = forms.IntegerField(
        required=False, min_value=0, help_text="Number of recurring charge periods (0 for no recurring charges)"
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

        # Check if this is an amendment (has previous_version)
        instance = kwargs.get('instance')
        initial = kwargs.get('initial') or {}

        # Check for previous_version in initial data (from clone URL)
        has_previous_version_in_initial = 'previous_version' in initial and initial['previous_version']
        has_previous_version_on_instance = instance and hasattr(instance, 'previous_version') and instance.previous_version

        is_amendment = (instance and instance.pk is None) and (has_previous_version_in_initial or has_previous_version_on_instance)

        # Store this flag for use in clean()
        self._is_amendment = is_amendment

        if is_amendment:
            # For amendments, make currency read-only
            self.fields['charge_currency'].disabled = True
            self.fields['charge_currency'].help_text = "Currency cannot be changed in amendments (inherited from original contract)"
        else:
            # For new contracts, make recurring charges required
            self.fields['recurring_charge'].required = True
            self.fields['recurring_charge_period'].required = True
            self.fields['number_of_recurring_charges'].required = True
            self.fields['number_of_recurring_charges'].min_value = 1

    def clean(self):
        cleaned_data = super().clean()

        # If super().clean() returned None (validation errors), return early
        if cleaned_data is None:
            return cleaned_data

        # Use the flag set in __init__ to determine if this is an amendment
        is_new_contract = not getattr(self, '_is_amendment', False) and not self.instance.pk

        # For new contracts (not amendments), require recurring charge fields
        if is_new_contract:
            recurring_charge = cleaned_data.get('recurring_charge')
            recurring_charge_period = cleaned_data.get('recurring_charge_period')
            number_of_recurring_charges = cleaned_data.get('number_of_recurring_charges')

            if not recurring_charge:
                self.add_error('recurring_charge', 'This field is required for new contracts.')
            if not recurring_charge_period:
                self.add_error('recurring_charge_period', 'This field is required for new contracts.')
            if number_of_recurring_charges is None:
                self.add_error('number_of_recurring_charges', 'This field is required for new contracts.')
            elif number_of_recurring_charges < 1:
                self.add_error('number_of_recurring_charges', 'Must be at least 1 for new contracts.')

        return cleaned_data

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


class ContractInfoFilterForm(NetBoxModelFilterSetForm):
    """Filter form for ContractInfo list views"""

    model = ContractInfo

    # Text search (inherited from base, just needs to be defined)
    contract_number = forms.CharField(
        required=False,
        label="Contract Number"
    )

    contract_type = forms.MultipleChoiceField(
        required=False,
        choices=ContractTypeChoices,
        label="Contract Type"
    )

    # Financial filters
    charge_currency = forms.MultipleChoiceField(
        required=False,
        choices=CurrencyChoices,
        label="Currency"
    )

    recurring_charge_period = forms.MultipleChoiceField(
        required=False,
        choices=RecurringChargePeriodChoices,
        label="Recurring Charge Period"
    )

    # Date filters
    effective_date = forms.DateField(
        required=False,
        label="Effective Date",
        widget=forms.DateInput(attrs={"type": "date"})
    )

    start_date = forms.DateField(
        required=False,
        label="Start Date",
        widget=forms.DateInput(attrs={"type": "date"})
    )

    end_date = forms.DateField(
        required=False,
        label="End Date",
        widget=forms.DateInput(attrs={"type": "date"})
    )

    commitment_end_date = forms.DateField(
        required=False,
        label="Commitment End Date",
        widget=forms.DateInput(attrs={"type": "date"})
    )

    # Version chain filters
    is_active = forms.NullBooleanField(
        required=False,
        label="Is Active",
        help_text="Show only active (not superseded) contracts",
        widget=forms.Select(
            choices=[
                ("", "All"),
                ("true", "Active"),
                ("false", "Superseded"),
            ]
        )
    )

    has_previous_version = forms.NullBooleanField(
        required=False,
        label="Has Previous Version",
        help_text="Filter by version chain status",
        widget=forms.Select(
            choices=[
                ("", "All"),
                ("true", "Has Previous Version"),
                ("false", "First Version (v1)"),
            ]
        )
    )

    # Segments filter
    segments = DynamicModelMultipleChoiceField(
        queryset=Segment.objects.all(),
        required=False,
        label="Segments",
        help_text="Filter by associated segments"
    )

    # Tags filter
    tag = TagFilterField(model)

    fieldsets = (
        FieldSet("q", "tag", "filter_id", name="General"),
        FieldSet(
            "contract_number",
            "contract_type",
            "is_active",
            "has_previous_version",
            name="Contract Details",
        ),
        FieldSet(
            "charge_currency",
            "recurring_charge_period",
            name="Financial",
        ),
        FieldSet(
            "effective_date",
            "start_date",
            "end_date",
            "commitment_end_date",
            name="Dates",
        ),
        FieldSet(
            "segments",
            name="Relationships",
        ),
    )