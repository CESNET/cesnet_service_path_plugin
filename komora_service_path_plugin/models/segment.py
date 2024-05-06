from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel
from django.core.exceptions import ValidationError


class Segment(NetBoxModel):
    name = models.CharField(max_length=255)
    network_label = models.CharField(max_length=255, null=True, blank=True)
    install_date = models.DateField(null=True, blank=True)
    termination_date = models.DateField(null=True, blank=True)

    supplier = models.ForeignKey(
        'tenancy.tenant',
        on_delete=models.PROTECT,
        null=False,
        blank=False)
    supplier_segment_id = models.CharField(
        max_length=255, null=True, blank=True)
    supplier_segment_name = models.CharField(
        max_length=255, null=True, blank=True)
    supplier_segment_contract = models.CharField(
        max_length=255, null=True, blank=True)

    site_a = models.ForeignKey(
        'dcim.site',
        on_delete=models.PROTECT,
        related_name='site_a',
        null=False,
        blank=False)
    location_a = models.ForeignKey(
        'dcim.location',
        on_delete=models.PROTECT,
        related_name='location_a',
        null=False,
        blank=False)
    device_a = models.ForeignKey(
        'dcim.device',
        on_delete=models.SET_NULL,
        related_name='device_a',
        null=True,
        blank=True)
    port_a = models.ForeignKey(
        'dcim.interface',
        on_delete=models.SET_NULL,
        related_name='port_a',
        null=True,
        blank=True)
    note_a = models.TextField(null=True, blank=True)

    site_b = models.ForeignKey(
        'dcim.site',
        on_delete=models.PROTECT,
        related_name='site_b',
        null=False,
        blank=False)
    location_b = models.ForeignKey(
        'dcim.location',
        on_delete=models.PROTECT,
        related_name='location_b',
        null=False,
        blank=False)
    device_b = models.ForeignKey(
        'dcim.device',
        on_delete=models.SET_NULL,
        related_name='device_b',
        null=True,
        blank=True)
    port_b = models.ForeignKey(
        'dcim.interface',
        on_delete=models.SET_NULL,
        related_name='port_b',
        null=True,
        blank=True)
    note_b = models.TextField(null=True, blank=True)

    imported_data = models.JSONField(null=True, blank=True)

    # TODO:
    # technology
    # SLA

    # TODO:
    # Contacts
    # Notes
    # Documents
    # Attachments

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "plugins:komora_service_path_plugin:segment",
            args=[
                self.pk])

    def validate_location_in_site(self, location, site, field_name):
        if location and location.site != site:
            raise ValidationError(
                {field_name: f"Location must be in Site: {site}"}
            )

    def validate_port_in_device(self, port, device, field_name):
        if port and port.device != device:
            raise ValidationError(
                {field_name: f"Port must be in Device: {device}"}
            )

    def clean(self):
        super().clean()

        self.validate_location_in_site(
            self.location_a, self.site_a, 'location_a')
        self.validate_location_in_site(
            self.location_b, self.site_b, 'location_b')

        self.validate_port_in_device(self.port_a, self.device_a, 'port_a')
        self.validate_port_in_device(self.port_b, self.device_b, 'port_b')

        # TODO:
        # validate if device is located on site or location?
