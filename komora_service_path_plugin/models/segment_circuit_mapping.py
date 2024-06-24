from circuits.models import Circuit
from django.db import models
from django.urls import reverse
from komora_service_path_plugin.models import Segment
from netbox.models import NetBoxModel


class SegmentCircuitMapping(NetBoxModel):
    segment = models.ForeignKey(
        Segment, on_delete=models.CASCADE, null=False, blank=False
    )
    circuit = models.ForeignKey(
        Circuit, on_delete=models.CASCADE, null=False, blank=False
    )

    class Meta:
        ordering = ("segment", "circuit")
        unique_together = ("segment", "circuit")

    def __str__(self):
        return f"{self.segment} - {self.circuit}"

    def get_absolute_url(self):
        return reverse("circuits:circuit", args=[self.circuit.pk],)
