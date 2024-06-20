from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel
from komora_service_path_plugin.models import Segment
from circuits.models import Circuit


class ServicePath(NetBoxModel):
    name = models.CharField(max_length=225)
    state = models.CharField(
        max_length=225
    )  # TODO: maybe choice field? Or extra table? (I don't like extra table)
    kind = models.CharField(
        max_length=225
    )  # TODO: maybe choice field? Or extra table? (I don't like extra table)

    segments = models.ManyToManyField(Segment, through="ServicePathSegmentMapping")
    circuits = models.ManyToManyField(Circuit, through="ServicePathCircuitMapping")

    # Komora fields
    imported_data = models.JSONField(null=True, blank=True)
    komora_id = models.BigIntegerField(null=True, blank=True)  # TODO: change to False

    class Meta:
        ordering = ("name", "state", "kind")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:komora_service_path_plugin:servicepath", args=[self.pk])
