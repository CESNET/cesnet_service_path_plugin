from circuits.models import Circuit
from django.db import models
from django.urls import reverse
from komora_service_path_plugin.models import ServicePath
from netbox.models import NetBoxModel


class ServicePathCircuitMapping(NetBoxModel):
    service_path = models.ForeignKey(
        ServicePath, on_delete=models.CASCADE, null=False, blank=False
    )
    circuit = models.ForeignKey(
        Circuit, on_delete=models.CASCADE, null=False, blank=False
    )

    class Meta:
        ordering = ("service_path", "circuit")
        unique_together = ("service_path", "circuit")

    def __str__(self):
        return f"{self.service_path} - {self.circuit}"

    def get_absolute_url(self):
        return reverse("circuits:circuit", args=[self.circuit.pk],)
