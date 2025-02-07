from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel

from cesnet_service_path_plugin.models import Segment
from cesnet_service_path_plugin.models.sync_status_choices import SyncStatusChoices

STATE_CHOICES = [("active", "Aktivní"), ("planned", "Plánovaný"), ("decommissioned", "Decommissioned")]
KIND_CHOICES = [("experimental", "Experimentální"), ("core", "Páteřní"), ("customer", "Zákaznická")]


class ServicePath(NetBoxModel):
    name = models.CharField(max_length=225)
    state = models.CharField(max_length=225)  # TODO: maybe choice field? Or extra table? (I don't like extra table)
    kind = models.CharField(max_length=225)  # TODO: maybe choice field? Or extra table? (I don't like extra table)
    sync_status = models.CharField(
        max_length=30,
        choices=SyncStatusChoices,
        blank=False,
        default="active",
    )

    segments = models.ManyToManyField(Segment, through="ServicePathSegmentMapping")

    comments = models.TextField(verbose_name="Comments", blank=True)

    class Meta:
        ordering = ("name", "state", "kind")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:cesnet_service_path_plugin:servicepath", args=[self.pk])

    def get_sync_status_color(self):
        return SyncStatusChoices.colors.get(self.sync_status)
