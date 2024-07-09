from django import forms
from netbox.forms import NetBoxModelFilterSetForm

from komora_service_path_plugin.models import Segment


class SegmentFilterForm(NetBoxModelFilterSetForm):
    model = Segment

    name = forms.CharField(required=False)
    # TODO:
    fieldsets = (
        # (None, ("filter_id", "q")),
        ("Related Objects", ("name", )),
    )
