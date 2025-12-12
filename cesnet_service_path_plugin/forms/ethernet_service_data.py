from django import forms
from netbox.forms import NetBoxModelForm
from utilities.forms import add_blank_choice
from utilities.forms.fields import CommentField
from utilities.forms.rendering import FieldSet

from cesnet_service_path_plugin.models import EthernetServiceSegmentData
from cesnet_service_path_plugin.models.custom_choices import (
    EncapsulationTypeChoices,
    InterfaceTypeChoices,
)


class EthernetServiceSegmentDataForm(NetBoxModelForm):
    """
    Form for creating/editing Ethernet Service technical data.

    This form is used to add or modify technical specifications for Ethernet segments.
    The segment is set automatically based on the context (URL parameter).
    """

    encapsulation_type = forms.ChoiceField(
        choices=add_blank_choice(EncapsulationTypeChoices),
        required=False,
        label="Encapsulation Type",
        help_text="Ethernet encapsulation and tagging method",
    )

    interface_type = forms.ChoiceField(
        choices=add_blank_choice(InterfaceTypeChoices),
        required=False,
        label="Interface Type",
        help_text="Physical interface form factor",
    )

    comments = CommentField()

    class Meta:
        model = EthernetServiceSegmentData
        fields = [
            'port_speed',
            'vlan_id',
            'vlan_tags',
            'encapsulation_type',
            'interface_type',
            'mtu_size',
            'comments',
        ]

    fieldsets = (
        FieldSet('port_speed', 'interface_type', 'mtu_size', name='Port Specifications'),
        FieldSet('vlan_id', 'vlan_tags', 'encapsulation_type', name='VLAN Configuration'),
    )
