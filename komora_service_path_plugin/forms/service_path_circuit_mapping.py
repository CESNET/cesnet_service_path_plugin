from django import forms
from ipam.models import Prefix
from circuits.models import Circuit
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import CommentField, DynamicModelChoiceField
from utilities.querysets import RestrictedQuerySet
from komora_service_path_plugin.models import ServicePathCircuitMapping, ServicePath
from circuits.models import Circuit


class ServicePathCircuitMappingForm(NetBoxModelForm):
    service_path = DynamicModelChoiceField(
        queryset=ServicePath.objects.all(), required=True, selector=True)

    circuit = DynamicModelChoiceField(
        queryset=Circuit.objects.all(), required=True, disabled_indicator='circuit_id', disabled=True)

    class Meta:
        model = ServicePathCircuitMapping
        fields = ("service_path", "circuit")


class ServicePathCircuitMappingFilterForm(NetBoxModelFilterSetForm):
    model = ServicePathCircuitMapping

    service_path = DynamicModelChoiceField(
        queryset=ServicePath.objects.all(), required=True)

    circuit = DynamicModelChoiceField(
        queryset=Circuit.objects.all(), required=True)

    fieldsets = (
        (None, ("filter_id", "q")),
        ("Related Objects", ("service_path", "circuit")),
    )
