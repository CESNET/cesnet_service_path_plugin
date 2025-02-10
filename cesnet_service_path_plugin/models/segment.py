from circuits.models import Circuit
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel

from cesnet_service_path_plugin.models.custom_choices import StatusChoices


class Segment(NetBoxModel):
    name = models.CharField(max_length=255)
    network_label = models.CharField(max_length=255, null=True, blank=True)
    install_date = models.DateField(null=True, blank=True)
    termination_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=30,
        choices=StatusChoices,
        default=StatusChoices.ACTIVE,
        blank=False,
        null=False,
    )

    provider = models.ForeignKey(
        "circuits.provider",
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        related_name="+",
    )
    provider_segment_id = models.CharField(max_length=255, null=True, blank=True)
    provider_segment_name = models.CharField(max_length=255, null=True, blank=True)
    provider_segment_contract = models.CharField(max_length=255, null=True, blank=True)

    site_a = models.ForeignKey(
        "dcim.site",
        on_delete=models.PROTECT,
        related_name="+",
        null=False,
        blank=False,
    )
    location_a = models.ForeignKey(
        "dcim.location",
        on_delete=models.PROTECT,
        related_name="+",
        null=False,
        blank=False,
    )

    site_b = models.ForeignKey(
        "dcim.site",
        on_delete=models.PROTECT,
        related_name="+",
        null=False,
        blank=False,
    )
    location_b = models.ForeignKey(
        "dcim.location",
        on_delete=models.PROTECT,
        related_name="+",
        null=False,
        blank=False,
    )

    # Circuit
    circuits = models.ManyToManyField(Circuit, through="SegmentCircuitMapping")
    comments = models.TextField(verbose_name="Comments", blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:cesnet_service_path_plugin:segment", args=[self.pk])

    def validate_location_in_site(self, location, site, field_name):
        if location and location.site != site:
            raise ValidationError({field_name: f"Location must be in Site: {site}"})

    def clean(self):
        super().clean()

        self.validate_location_in_site(self.location_a, self.site_a, "location_a")
        self.validate_location_in_site(self.location_b, self.site_b, "location_b")

    def get_status_color(self):
        return StatusChoices.colors.get(self.status, "gray")
