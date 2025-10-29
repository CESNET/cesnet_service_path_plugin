from circuits.models import Circuit
from netbox.forms import NetBoxModelBulkEditForm, NetBoxModelForm
from utilities.forms.fields import DynamicModelChoiceField
from utilities.forms.rendering import FieldSet

from cesnet_service_path_plugin.models import Segment, SegmentCircuitMapping


# In segment_circuit_mapping.py
class SegmentCircuitMappingForm(NetBoxModelForm):
    segment = DynamicModelChoiceField(queryset=Segment.objects.all(), required=True, selector=True)
    circuit = DynamicModelChoiceField(queryset=Circuit.objects.all(), required=True, selector=True)

    class Meta:
        model = SegmentCircuitMapping
        fields = ("segment", "circuit")


class SegmentCircuitMappingBulkEditForm(NetBoxModelBulkEditForm):
    segment = DynamicModelChoiceField(queryset=Segment.objects.all(), required=False)
    circuit = DynamicModelChoiceField(queryset=Circuit.objects.all(), required=False)

    model = SegmentCircuitMapping
    fieldsets = (FieldSet("segment", "circuit", name="Segment Circuit Mapping"),)
    nullable_fields = ()
