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

    wavelength = forms.DecimalField(
        required=False,
        label="Wavelength",
        help_text="Center wavelength in nanometers (C-band: 1530-1565nm, L-band: 1565-1625nm)",
    )

    spectral_slot_width = forms.DecimalField(
        required=False,
        label="Spectral slot width",
        help_text="Optical channel bandwidth (GHz)",
    )

    itu_grid_position = forms.IntegerField(
        required=False,
        label="ITU grid position",
        help_text="ITU-T G.694.1 standard channel number (0 = 193.1 THz)",
    )

    chromatic_dispersion = forms.DecimalField(
        required=False,
        label="Chromatic dispersion",
        help_text="Chromatic dispersion at the operating wavelength (ps/nm)",
    )

    pmd_tolerance = forms.DecimalField(
        required=False,
        label="PMD tolerance",
        help_text="Polarization mode dispersion tolerance (ps)",
    )

    modulation_format = forms.ChoiceField(
        choices=add_blank_choice(ModulationFormatChoices),
        required=False,
        label="Modulation format",
        help_text="Digital modulation format",
    )

    comments = CommentField()

    class Meta:
        model = OpticalSpectrumSegmentData
        fields = [
            "wavelength",
            "spectral_slot_width",
            "itu_grid_position",
            "chromatic_dispersion",
            "pmd_tolerance",
            "modulation_format",
            "comments",
        ]

    fieldsets = (
        FieldSet("wavelength", "spectral_slot_width", "itu_grid_position", name="Wavelength specifications"),
        FieldSet("chromatic_dispersion", "pmd_tolerance", "modulation_format", name="Signal characteristics"),
    )
