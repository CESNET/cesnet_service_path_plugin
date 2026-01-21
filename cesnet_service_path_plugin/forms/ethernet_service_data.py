from django import forms
from netbox.forms import NetBoxModelForm
from utilities.forms import add_blank_choice
from utilities.forms.fields import CommentField
from utilities.forms.rendering import FieldSet
from dcim.choices import InterfaceTypeChoices

from cesnet_service_path_plugin.models import EthernetServiceSegmentData
from cesnet_service_path_plugin.models.custom_choices import EncapsulationTypeChoices


class EthernetServiceSegmentDataForm(NetBoxModelForm):
    """
    Form for creating/editing Ethernet Service technical data.

    This form is used to add or modify technical specifications for Ethernet segments.
    The segment is set automatically based on the context (URL parameter).
    """

    port_speed = forms.IntegerField(
        required=False,
        label="Port speed",
        help_text="Ethernet port speed or service bandwidth (Mbps)",
    )

    vlan_id = forms.IntegerField(
        required=False,
        label="VLAN ID",
        help_text="Primary VLAN tag (1-4094)",
    )

    vlan_tags = forms.CharField(
        required=False,
        label="VLAN tags",
        help_text="Additional VLAN tags for QinQ or multiple VLANs (comma-separated)",
    )

    encapsulation_type = forms.ChoiceField(
        choices=add_blank_choice(EncapsulationTypeChoices),
        required=False,
        label="Encapsulation type",
        help_text="Ethernet encapsulation and tagging method",
    )

    interface_type = forms.ChoiceField(
        choices=add_blank_choice(InterfaceTypeChoices),
        required=False,
        label="Interface type",
        help_text="Physical interface form factor",
    )

    mtu_size = forms.IntegerField(
        required=False,
        label="MTU size",
        help_text="Maximum transmission unit size (bytes)",
    )

    comments = CommentField()

    class Meta:
        model = EthernetServiceSegmentData
        fields = [
            "port_speed",
            "vlan_id",
            "vlan_tags",
            "encapsulation_type",
            "interface_type",
            "mtu_size",
            "comments",
        ]

    fieldsets = (
        FieldSet("port_speed", "interface_type", "mtu_size", name="Port specifications"),
        FieldSet("vlan_id", "vlan_tags", "encapsulation_type", name="VLAN configuration"),
    )
