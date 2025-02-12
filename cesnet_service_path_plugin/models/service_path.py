from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel

from cesnet_service_path_plugin.models import Segment
from cesnet_service_path_plugin.models.custom_choices import KindChoices, StatusChoices


class ServicePath(NetBoxModel):
    name = models.CharField(max_length=225)
    status = models.CharField(
        max_length=30,
        choices=StatusChoices,
        default=StatusChoices.ACTIVE,
        blank=False,
        null=False,
    )

    kind = models.CharField(
        max_length=30,
        choices=KindChoices,
        default=KindChoices.CORE,
        blank=False,
        null=False,
    )

    segments = models.ManyToManyField(Segment, through="ServicePathSegmentMapping")
    comments = models.TextField(verbose_name="Comments", blank=True)

    class Meta:
        ordering = ("name", "status", "kind")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:cesnet_service_path_plugin:servicepath", args=[self.pk])

    def get_status_color(self):
        return StatusChoices.colors.get(self.status, "gray")

    def get_kind_color(self):
        return KindChoices.colors.get(self.kind, "gray")
