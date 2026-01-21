from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel
from dcim.choices import InterfaceTypeChoices

from .custom_choices import EncapsulationTypeChoices


class EthernetServiceSegmentData(NetBoxModel):
    """
    Technical data specific to Ethernet Service segments.

    This model stores detailed technical specifications for Ethernet connections,
    including port speed, VLAN configuration, encapsulation, interface type, and MTU.
    """

    segment = models.OneToOneField(
        "Segment",
        on_delete=models.CASCADE,
        related_name="ethernet_service_data",
        primary_key=True,
        help_text="Associated segment (1:1 relationship)",
    )

    port_speed = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MaxValueValidator(100000)],
        help_text="Ethernet port speed or service bandwidth (Mbps)",
    )

    vlan_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(4094)],
        help_text="Primary VLAN tag (1-4094)",
    )

    vlan_tags = models.CharField(
        max_length=255,
        blank=True,
        help_text="Additional VLAN tags for QinQ or multiple VLANs (comma-separated)",
    )

    encapsulation_type = models.CharField(
        max_length=50,
        blank=True,
        choices=EncapsulationTypeChoices,
        help_text="Ethernet encapsulation and tagging method",
    )

    interface_type = models.CharField(
        max_length=30,
        blank=True,
        choices=InterfaceTypeChoices,
        help_text="Physical interface form factor",
    )

    mtu_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(64), MaxValueValidator(16000)],
        help_text="Maximum transmission unit size (bytes)",
    )

    class Meta:
        ordering = ("segment",)
        verbose_name = "Ethernet Service Technical Data"
        verbose_name_plural = "Ethernet Service Technical Data"

    def __str__(self):
        try:
            if self.port_speed:
                return f"Ethernet Service Data for {self.segment.name} ({self.port_speed} Mbps)"
            return f"Ethernet Service Data for {self.segment.name}"
        except Exception:
            if self.port_speed:
                return f"Ethernet Service Data (segment #{self.pk}, {self.port_speed} Mbps)"
            return f"Ethernet Service Data (segment #{self.pk})"

    def get_absolute_url(self):
        # Redirect to the parent segment's detail page
        return reverse("plugins:cesnet_service_path_plugin:segment", args=[self.segment.pk])

    def clean(self):
        """Additional validation for Ethernet service data"""
        from django.core.exceptions import ValidationError

        super().clean()

        errors = {}

        # Validate VLAN ID is within standard range if specified
        if self.vlan_id is not None:
            if self.vlan_id == 0:
                errors["vlan_id"] = "VLAN ID 0 is reserved (priority tagging)"
            elif self.vlan_id == 4095:
                errors["vlan_id"] = "VLAN ID 4095 is reserved"

        # Validate MTU size for common configurations
        if self.mtu_size:
            # Standard Ethernet: 1500
            # Jumbo frames: typically 9000 or 9216
            # Some providers allow up to 16000
            if self.mtu_size < 576:
                # Minimum MTU for IP
                errors["mtu_size"] = "MTU size should be at least 576 bytes for IP"

        # Validate vlan_tags format if present (optional, informational check)
        if self.vlan_tags:
            tags = self.vlan_tags.split(",")
            for tag in tags:
                tag = tag.strip()
                if tag:
                    try:
                        vlan_num = int(tag)
                        if vlan_num < 1 or vlan_num > 4094:
                            errors["vlan_tags"] = f"Invalid VLAN tag '{tag}': must be 1-4094"
                            break
                    except ValueError:
                        errors["vlan_tags"] = f"Invalid VLAN tag '{tag}': must be numeric"
                        break

        if errors:
            raise ValidationError(errors)
