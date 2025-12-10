from django import forms
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import DynamicModelMultipleChoiceField, TagFilterField
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets import DatePicker

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

    charge_currency = forms.ChoiceField(
        required=False, choices=CurrencyChoices, help_text="Currency for all charges (cannot be changed in amendments)"
    )

    non_recurring_charge = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        help_text="One-time fees for this version (setup, installation, etc.)",
    )

    recurring_charge = forms.DecimalField(
        max_digits=10, decimal_places=2, required=False, help_text="Recurring fee amount (optional)"
    )

    recurring_charge_period = forms.ChoiceField(
        required=False, choices=RecurringChargePeriodChoices, help_text="Frequency of recurring charges"
    )

    number_of_recurring_charges = forms.IntegerField(
        required=False, min_value=0, help_text="Number of recurring charge periods (0 for no recurring charges)"
    )


    notes = forms.CharField(
        required=False, widget=forms.Textarea(attrs={"rows": 3}), help_text="Notes specific to this version"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Check if this is an amendment (has previous_version)
        instance = kwargs.get("instance")
        initial = kwargs.get("initial") or {}

        # Check for previous_version in initial data (from clone URL)
        has_previous_version_in_initial = "previous_version" in initial and initial["previous_version"]
        has_previous_version_on_instance = (
            instance and hasattr(instance, "previous_version") and instance.previous_version
        )

        is_amendment = (instance and instance.pk is None) and (
            has_previous_version_in_initial or has_previous_version_on_instance
        )

        # Store this flag for use in clean()
        self._is_amendment = is_amendment

        # Store the previous version for currency validation
        if has_previous_version_on_instance:
            self._previous_version = instance.previous_version
        elif has_previous_version_in_initial:
            # Get previous version from initial data
            try:
                prev_id = initial["previous_version"]
                if isinstance(prev_id, int) or (isinstance(prev_id, str) and prev_id.isdigit()):
                    self._previous_version = ContractInfo.objects.get(pk=int(prev_id))
                else:
                    self._previous_version = None
            except (ContractInfo.DoesNotExist, ValueError, KeyError):
                self._previous_version = None
        else:
            self._previous_version = None

        if is_amendment:
            # For amendments, make currency field disabled in the UI
            # Note: disabled fields don't submit values, but we handle this in clean_charge_currency()
            self.fields["charge_currency"].disabled = True
            self.fields["charge_currency"].help_text = (
                "Currency cannot be changed in amendments (inherited from original contract)"
            )

    def clean_charge_currency(self):
        """
        For amendments, enforce that currency matches the previous version.
        This prevents the issue where disabled fields don't submit values.
        """
        charge_currency = self.cleaned_data.get("charge_currency")

        # For amendments, always use the previous version's currency
        if self._is_amendment and self._previous_version:
            return self._previous_version.charge_currency

        return charge_currency

    def clean(self):
        """
        Custom validation for ContractInfo form.
        All fields are optional to allow creating contract stubs.
        """
        cleaned_data = super().clean()

        # Prevent cloning of non-active (superseded) contracts
        # This can happen if a user manually manipulates the URL
        if self.instance.pk is None:  # Only for new instances (create/clone)
            previous_version = self.instance.previous_version
            if previous_version and not previous_version.is_active:
                raise forms.ValidationError(
                    "Cannot create a new version from a superseded contract. "
                    f"Please clone from the active version (v{previous_version.get_latest_version().version}) instead."
                )

        return cleaned_data

    class Meta:
        model = ContractInfo
        fields = [
            "segments",
            "contract_number",
            "charge_currency",
            "non_recurring_charge",
            "recurring_charge",
            "recurring_charge_period",
            "number_of_recurring_charges",
            "start_date",
            "end_date",
            "notes",
        ]
        widgets = {
            "start_date": DatePicker(),
            "end_date": DatePicker(),
        }

    fieldsets = (
        FieldSet(
            "segments",
            name="Segments",
        ),
        FieldSet(
            "contract_number",
            name="Contract Metadata",
        ),
        FieldSet(
            "charge_currency",
            "non_recurring_charge",
            name="Charges",
        ),
        FieldSet(
            "recurring_charge",
            "recurring_charge_period",
            "number_of_recurring_charges",
            name="Recurring Charges",
        ),
        FieldSet(
            "start_date",
            "end_date",
            name="Dates",
        ),
        FieldSet(
            "notes",
            name="Notes",
        ),
    )


class ContractInfoFilterForm(NetBoxModelFilterSetForm):
    """Filter form for ContractInfo list views"""

    model = ContractInfo

    # Text search (inherited from base, just needs to be defined)
    contract_number = forms.CharField(required=False, label="Contract Number")

    contract_type = forms.MultipleChoiceField(required=False, choices=ContractTypeChoices, label="Contract Type")

    # Financial filters
    charge_currency = forms.MultipleChoiceField(required=False, choices=CurrencyChoices, label="Currency")

    recurring_charge_period = forms.MultipleChoiceField(
        required=False, choices=RecurringChargePeriodChoices, label="Recurring Charge Period"
    )

    # Date filters
    start_date = forms.DateField(required=False, label="Start Date", widget=forms.DateInput(attrs={"type": "date"}))

    end_date = forms.DateField(required=False, label="End Date", widget=forms.DateInput(attrs={"type": "date"}))

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
        ),
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
        ),
    )

    # Segments filter
    segments = DynamicModelMultipleChoiceField(
        queryset=Segment.objects.all(), required=False, label="Segments", help_text="Filter by associated segments"
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
            "start_date",
            "end_date",
            name="Dates",
        ),
        FieldSet(
            "segments",
            name="Relationships",
        ),
    )
