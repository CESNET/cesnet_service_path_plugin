from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel

from .custom_choices import (
    FiberJacketTypeChoices,
    FiberModeChoices,
    MultimodeFiberSubtypeChoices,
    SingleModeFiberSubtypeChoices,
)
from dcim.choices import PortTypeChoices


class DarkFiberSegmentData(NetBoxModel):
    """
    Technical data specific to Dark Fiber segments.

    This model stores detailed technical specifications for dark fiber connections,
    including fiber type, attenuation, loss, length, and connector information.
    """

    segment = models.OneToOneField(
        "Segment",
        on_delete=models.CASCADE,
        related_name="dark_fiber_data",
        primary_key=True,
        help_text="Associated segment (1:1 relationship)",
    )

    # NEW: Fiber Mode and Subtype
    fiber_mode = models.CharField(
        max_length=20,
        blank=True,
        choices=FiberModeChoices,
        help_text="Fiber mode: Single-mode (SMF) or Multimode (MMF)",
    )

    single_mode_subtype = models.CharField(
        max_length=20,
        blank=True,
        choices=SingleModeFiberSubtypeChoices,
        help_text="ITU-T single-mode fiber standard (G.652-G.657) - only for single-mode fibers",
    )

    multimode_subtype = models.CharField(
        max_length=20,
        blank=True,
        choices=MultimodeFiberSubtypeChoices,
        help_text="ISO/IEC multimode fiber standard (OM1-OM5) - only for multimode fibers",
    )

    # NEW: Jacket Type
    jacket_type = models.CharField(
        max_length=30,
        blank=True,
        choices=FiberJacketTypeChoices,
        help_text="Cable jacket/construction type (indoor/outdoor, armored, loose tube, etc.)",
    )

    # EXISTING: Fiber attenuation
    fiber_attenuation_max = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Maximum attenuation at 1550nm wavelength (dB/km)",
    )

    # EXISTING: Total loss
    total_loss = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="End-to-end optical loss including connectors and splices (dB)",
    )

    # EXISTING: Total length
    total_length = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10000)],
        help_text="Physical length of the fiber cable (km)",
    )

    # EXISTING: Number of fibers
    number_of_fibers = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MaxValueValidator(1000)],
        help_text="Total number of fiber strands in the cable",
    )

    # EXISTING: Connectors
    connector_type_side_a = models.CharField(
        max_length=30,
        blank=True,
        choices=PortTypeChoices,
        help_text="Optical connector type and polish (Side A)",
    )

    connector_type_side_b = models.CharField(
        max_length=30,
        blank=True,
        choices=PortTypeChoices,
        help_text="Optical connector type and polish (Side B)",
    )

    class Meta:
        ordering = ("segment",)
        verbose_name = "Dark Fiber Technical Data"
        verbose_name_plural = "Dark Fiber Technical Data"

    def __str__(self):
        try:
            return f"Dark Fiber Data for {self.segment.name}"
        except Exception:
            return f"Dark Fiber Data (segment #{self.pk})"

    def get_absolute_url(self):
        # Redirect to the parent segment's detail page
        return reverse("plugins:cesnet_service_path_plugin:segment", args=[self.segment.pk])

    def clean(self):
        """Validate fiber mode/subtype consistency"""
        from django.core.exceptions import ValidationError

        super().clean()

        errors = {}

        # Validate that single-mode subtype is only set for single-mode fibers
        if self.single_mode_subtype and self.fiber_mode != FiberModeChoices.SINGLE_MODE:
            errors["single_mode_subtype"] = (
                "Single-mode subtype can only be set when fiber mode is Single-mode"
            )

        # Validate that multimode subtype is only set for multimode fibers
        if self.multimode_subtype and self.fiber_mode != FiberModeChoices.MULTIMODE:
            errors["multimode_subtype"] = "Multimode subtype can only be set when fiber mode is Multimode"

        # Warn if fiber mode is set but no subtype is specified (not an error, just inconsistent)
        if self.fiber_mode == FiberModeChoices.SINGLE_MODE and not self.single_mode_subtype:
            # This is OK - user might not know the exact subtype
            pass

        if self.fiber_mode == FiberModeChoices.MULTIMODE and not self.multimode_subtype:
            # This is OK - user might not know the exact subtype
            pass

        if errors:
            raise ValidationError(errors)
