from django import forms
from netbox.forms import NetBoxModelForm
from utilities.forms import add_blank_choice
from utilities.forms.fields import CommentField
from utilities.forms.rendering import FieldSet

from cesnet_service_path_plugin.models import OpticalSpectrumSegmentData
from cesnet_service_path_plugin.models.custom_choices import ModulationFormatChoices


class OpticalSpectrumSegmentDataForm(NetBoxModelForm):
    """
    Form for creating/editing Optical Spectrum technical data.

    This form is used to add or modify technical specifications for DWDM/CWDM segments.
    The segment is set automatically based on the context (URL parameter).
    """

    modulation_format = forms.ChoiceField(
        choices=add_blank_choice(ModulationFormatChoices),
        required=False,
        label="Modulation Format",
        help_text="Digital modulation format",
    )

    comments = CommentField()

    class Meta:
        model = OpticalSpectrumSegmentData
        fields = [
            'wavelength',
            'spectral_slot_width',
            'itu_grid_position',
            'chromatic_dispersion',
            'pmd_tolerance',
            'modulation_format',
            'comments',
        ]

    fieldsets = (
        FieldSet('wavelength', 'spectral_slot_width', 'itu_grid_position', name='Wavelength Specifications'),
        FieldSet('chromatic_dispersion', 'pmd_tolerance', 'modulation_format', name='Signal Characteristics'),
    )
