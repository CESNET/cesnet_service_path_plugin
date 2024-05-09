from .segment import Segment
from .service_path import ServicePath
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel


class ServicePathSegmentMapping(NetBoxModel):
    service_path = models.ForeignKey(
        ServicePath, on_delete=models.CASCADE, null=False, blank=False
    )
    segment = models.ForeignKey(
        Segment, on_delete=models.CASCADE, null=False, blank=False
    )
    index = models.IntegerField(null=False, blank=False, default=0)

    # Komora fields
    imported_data = models.JSONField(null=True, blank=True)
    komora_id = models.BigIntegerField(null=True, blank=True)  # TODO: change to False

    class Meta:
        ordering = ("service_path", "segment", "index")
        unique_together = ("service_path", "segment", "index")

    def __str__(self):
        return f"{self.service_path} - {self.segment} - {self.index}"

    def get_absolute_url(self):
        return reverse(
            "plugins:komora_service_path_plugin:servicepathsegmentmapping",
            args=[self.pk],
        )
