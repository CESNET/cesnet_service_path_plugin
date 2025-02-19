from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel

from .segment import Segment
from .service_path import ServicePath


class ServicePathSegmentMapping(NetBoxModel):
    service_path = models.ForeignKey(
        ServicePath, on_delete=models.CASCADE, null=False, blank=False
    )
    segment = models.ForeignKey(
        Segment, on_delete=models.CASCADE, null=False, blank=False
    )

    class Meta:
        ordering = ("service_path", "segment")
        unique_together = ("service_path", "segment")

    def __str__(self):
        return f"{self.service_path} - {self.segment}"

    def get_absolute_url(self):
        return reverse(
            "plugins:cesnet_service_path_plugin:servicepathsegmentmapping",
            args=[self.pk],
        )
