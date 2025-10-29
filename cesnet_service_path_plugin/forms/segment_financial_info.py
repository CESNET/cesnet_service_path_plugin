from django import forms
from netbox.forms import NetBoxModelForm
from utilities.forms.fields import DynamicModelChoiceField
from utilities.forms.rendering import FieldSet

from cesnet_service_path_plugin.models import Segment, SegmentFinancialInfo
from cesnet_service_path_plugin.models.segment_financial_info import get_currency_choices, get_default_currency


class SegmentFinancialInfoForm(NetBoxModelForm):
    segment = DynamicModelChoiceField(
        queryset=Segment.objects.all(),
        required=True,
        selector=True,
        help_text="The segment this financial information belongs to",
    )

    monthly_charge = forms.DecimalField(
        max_digits=10, decimal_places=2, required=True, help_text="Fixed monthly fee for the service lease"
    )

    charge_currency = forms.ChoiceField(required=True, help_text="Currency for all charges")

    non_recurring_charge = forms.DecimalField(
        max_digits=10, decimal_places=2, required=False, help_text="One-time setup or installation fee"
    )

    commitment_period_months = forms.IntegerField(
        required=False, min_value=0, help_text="Number of months the contract cannot be terminated"
    )

    notes = forms.CharField(
        required=False, widget=forms.Textarea(attrs={"rows": 3}), help_text="Additional financial notes"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamically set currency choices from the model's get_currency_choices
        self.fields["charge_currency"].choices = get_currency_choices()
        self.fields["charge_currency"].initial = get_default_currency()

    class Meta:
        model = SegmentFinancialInfo
        fields = [
            "segment",
            "monthly_charge",
            "charge_currency",
            "non_recurring_charge",
            "commitment_period_months",
            "notes",
        ]

    fieldsets = (
        FieldSet(
            "segment",
            name="Segment",
        ),
        FieldSet(
            "monthly_charge",
            "charge_currency",
            "non_recurring_charge",
            name="Charges",
        ),
        FieldSet(
            "commitment_period_months",
            name="Commitment",
        ),
        FieldSet(
            "notes",
            name="Notes",
        ),
    )
