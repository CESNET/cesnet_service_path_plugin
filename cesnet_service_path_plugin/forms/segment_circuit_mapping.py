from circuits.models import Circuit
from netbox.forms import NetBoxModelForm
from utilities.forms.fields import DynamicModelChoiceField

from cesnet_service_path_plugin.models import Segment, SegmentCircuitMapping


# In segment_circuit_mapping.py
class SegmentCircuitMappingForm(NetBoxModelForm):
    segment = DynamicModelChoiceField(queryset=Segment.objects.all(), required=True, selector=True)
    circuit = DynamicModelChoiceField(queryset=Circuit.objects.all(), required=True, selector=True)

    class Meta:
        model = SegmentCircuitMapping
        fields = ("segment", "circuit")
