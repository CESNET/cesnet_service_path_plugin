from circuits.models import Circuit
from netbox.forms import NetBoxModelForm
from utilities.forms.fields import DynamicModelChoiceField

from komora_service_path_plugin.models import Segment, SegmentCircuitMapping


# From Circuit to Segment
class SegmentCircuitMappingForm(NetBoxModelForm):
    segment = DynamicModelChoiceField(
        queryset=Segment.objects.all(),
        required=True,
        selector=True,
        disabled_indicator="segment_id",
        # disabled=True
    )

    circuit = DynamicModelChoiceField(
        queryset=Circuit.objects.all(),
        required=True,
        disabled_indicator="circuit_id",
        selector=True,
        # disabled=True
    )

    class Meta:
        model = SegmentCircuitMapping
        fields = ("segment", "circuit")
