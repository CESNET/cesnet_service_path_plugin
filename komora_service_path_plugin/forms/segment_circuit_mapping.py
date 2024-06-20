from django import forms
from ipam.models import Prefix
from circuits.models import Circuit
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import CommentField, DynamicModelChoiceField
from utilities.querysets import RestrictedQuerySet
from komora_service_path_plugin.models import SegmentCircuitMapping, Segment
from circuits.models import Circuit


class SegmentCircuitMappingForm(NetBoxModelForm):
    segment = DynamicModelChoiceField(
        queryset=Segment.objects.all(), required=True, selector=True)
    
    circuit = DynamicModelChoiceField(
        queryset=Circuit.objects.all(), required=True, selector=True)

    class Meta:
        model = SegmentCircuitMapping
        fields = ("segment", "circuit")
