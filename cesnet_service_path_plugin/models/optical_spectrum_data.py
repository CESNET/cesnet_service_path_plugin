from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel

from .custom_choices import ModulationFormatChoices


class OpticalSpectrumSegmentData(NetBoxModel):
    """
    Technical data specific to Optical Spectrum (DWDM/CWDM) segments.

    This model stores detailed technical specifications for optical wavelength channels,
    including wavelength, spectral characteristics, dispersion, and modulation format.
    """

    segment = models.OneToOneField(
        "Segment",
        on_delete=models.CASCADE,
        related_name="optical_spectrum_data",
        primary_key=True,
        help_text="Associated segment (1:1 relationship)",
    )

    wavelength = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        null=True,
        blank=True,
        validators=[MinValueValidator(1260), MaxValueValidator(1625)],
        help_text="Center wavelength in nanometers (C-band: 1530-1565nm, L-band: 1565-1625nm)",
    )

    spectral_slot_width = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(1000)],
        help_text="Optical channel bandwidth (GHz)",
    )

    itu_grid_position = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(-100), MaxValueValidator(100)],
        help_text="ITU-T G.694.1 standard channel number (0 = 193.1 THz)",
    )

    chromatic_dispersion = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        null=True,
        blank=True,
        validators=[MinValueValidator(-100000), MaxValueValidator(100000)],
        help_text="Chromatic dispersion at the operating wavelength (ps/nm)",
    )

    pmd_tolerance = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Polarization mode dispersion tolerance (ps)",
    )

    modulation_format = models.CharField(
        max_length=30,
        blank=True,
        choices=ModulationFormatChoices,
        help_text="Digital modulation format",
    )

    class Meta:
        ordering = ("segment",)
        verbose_name = "Optical Spectrum Technical Data"
        verbose_name_plural = "Optical Spectrum Technical Data"

    def __str__(self):
        try:
            if self.wavelength:
                return f"Optical Spectrum Data for {self.segment.name} ({self.wavelength}nm)"
            return f"Optical Spectrum Data for {self.segment.name}"
        except Exception:
            if self.wavelength:
                return f"Optical Spectrum Data (segment #{self.pk}, {self.wavelength}nm)"
            return f"Optical Spectrum Data (segment #{self.pk})"

    def get_absolute_url(self):
        # Redirect to the parent segment's detail page
        return reverse("plugins:cesnet_service_path_plugin:segment", args=[self.segment.pk])

    def clean(self):
        """Additional validation for optical spectrum data"""
        from django.core.exceptions import ValidationError

        super().clean()

        errors = {}

        # Validate wavelength bands
        if self.wavelength:
            if 1530 <= self.wavelength <= 1565:
                # C-band - most common
                pass
            elif 1565 < self.wavelength <= 1625:
                # L-band
                pass
            elif 1260 <= self.wavelength < 1530:
                # O-band, E-band, S-band (less common but valid)
                pass
            # If outside these ranges, validators will catch it

        # If ITU grid position is specified, we could calculate expected wavelength
        # 193.1 THz (1552.52 nm) is position 0, with 100 GHz spacing
        # But this is informational, not enforced

        if errors:
            raise ValidationError(errors)
