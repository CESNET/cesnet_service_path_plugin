from django import forms
from ipam.models import Prefix
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import CommentField, DynamicModelChoiceField

from ..models import Segment


class SegmentForm(NetBoxModelForm):
    class Meta:
        model = Segment
        fields = ("name", "tags")


class SegmentFilterForm(NetBoxModelFilterSetForm):
    model = Segment

    name = forms.CharField(required=False)
    # TODO:
    fieldsets = (
        #(None, ("filter_id", "q")),
        ("Related Objects", ("name", )),
    )
