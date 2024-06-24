from circuits.models import Circuit
from komora_service_path_plugin.models import Segment, SegmentCircuitMapping
from netbox.forms import NetBoxModelForm
from utilities.forms.fields import DynamicModelChoiceField


class SegmentCircuitMappingForm(NetBoxModelForm):
    segment = DynamicModelChoiceField(
        queryset=Segment.objects.all(), required=True, selector=True)

    circuit = DynamicModelChoiceField(
        queryset=Circuit.objects.all(), required=True, disabled_indicator='circuit_id', disabled=True)

    class Meta:
        model = SegmentCircuitMapping
        fields = ("segment", "circuit")
