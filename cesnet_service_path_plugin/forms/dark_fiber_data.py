from django import forms
from netbox.forms import NetBoxModelForm
from utilities.forms import add_blank_choice
from utilities.forms.fields import CommentField
from utilities.forms.rendering import FieldSet

from cesnet_service_path_plugin.models import DarkFiberSegmentData
from cesnet_service_path_plugin.models.custom_choices import (
    ConnectorTypeChoices,
    FiberJacketTypeChoices,
    FiberModeChoices,
    MultimodeFiberSubtypeChoices,
    SingleModeFiberSubtypeChoices,
)


class DarkFiberSegmentDataForm(NetBoxModelForm):
    """
    Form for creating/editing Dark Fiber technical data.

    This form is used to add or modify technical specifications for dark fiber segments.
    The segment is set automatically based on the context (URL parameter).
    """

    fiber_mode = forms.ChoiceField(
        choices=add_blank_choice(FiberModeChoices),
        required=False,
        label="Fiber Mode",
        help_text="Single-mode (SMF) or Multimode (MMF)",
    )

    single_mode_subtype = forms.ChoiceField(
        choices=add_blank_choice(SingleModeFiberSubtypeChoices),
        required=False,
        label="Single-mode Subtype",
        help_text="ITU-T single-mode fiber standard (G.652-G.657)",
    )

    multimode_subtype = forms.ChoiceField(
        choices=add_blank_choice(MultimodeFiberSubtypeChoices),
        required=False,
        label="Multimode Subtype",
        help_text="ISO/IEC multimode fiber standard (OM1-OM5)",
    )

    jacket_type = forms.ChoiceField(
        choices=add_blank_choice(FiberJacketTypeChoices),
        required=False,
        label="Jacket Type",
        help_text="Cable jacket/construction type",
    )

    connector_type_side_a = forms.ChoiceField(
        choices=add_blank_choice(ConnectorTypeChoices),
        required=False,
        label="Connector Type (Side A)",
        help_text="Optical connector type and polish",
    )

    connector_type_side_b = forms.ChoiceField(
        choices=add_blank_choice(ConnectorTypeChoices),
        required=False,
        label="Connector Type (Side B)",
        help_text="Optical connector type and polish",
    )

    comments = CommentField()

    class Meta:
        model = DarkFiberSegmentData
        fields = [
            'fiber_mode',
            'single_mode_subtype',
            'multimode_subtype',
            'jacket_type',
            'fiber_attenuation_max',
            'total_loss',
            'total_length',
            'number_of_fibers',
            'connector_type_side_a',
            'connector_type_side_b',
            'comments',
        ]

    fieldsets = (
        FieldSet('fiber_mode', 'single_mode_subtype', 'multimode_subtype', 'jacket_type', name='Fiber Specifications'),
        FieldSet('fiber_attenuation_max', 'total_loss', 'total_length', 'number_of_fibers', name='Measurements'),
        FieldSet('connector_type_side_a', 'connector_type_side_b', name='Connectors'),
    )
