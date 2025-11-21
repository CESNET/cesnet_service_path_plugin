from django import forms
from netbox.forms import NetBoxModelForm
from utilities.forms.fields import DynamicModelChoiceField
from utilities.forms.rendering import FieldSet

from cesnet_service_path_plugin.models import Segment, ContractInfo, CurrencyChoices


class ContractInfoForm(NetBoxModelForm):
    segment = DynamicModelChoiceField(
        queryset=Segment.objects.all(),
        required=True,
        selector=True,
        help_text="The segment this contract information belongs to",
    )

    recurring_charge = forms.DecimalField(
        max_digits=10, decimal_places=2, required=True, help_text="Fixed monthly fee for the service lease"
    )

    charge_currency = forms.ChoiceField(required=True, help_text="Currency for all charges", choices=CurrencyChoices)

    non_recurring_charge = forms.DecimalField(
        max_digits=10, decimal_places=2, required=False, help_text="One-time setup or installation fee"
    )

    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}), help_text="Additional notes")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = ContractInfo
        fields = [
            "segment",
            "recurring_charge",
            "charge_currency",
            "non_recurring_charge",
            "notes",
        ]

    fieldsets = (
        FieldSet(
            "segment",
            name="Segment",
        ),
        FieldSet(
            "recurring_charge",
            "charge_currency",
            "non_recurring_charge",
            name="Charges",
        ),
        FieldSet(
            "notes",
            name="Notes",
        ),
    )
