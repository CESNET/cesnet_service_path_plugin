from django import forms
from ipam.models import Prefix
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import CommentField, DynamicModelChoiceField

from ..models import Segment


class SegmentForm(NetBoxModelForm):
    class Meta:
        model = Segment
        fields = ("name", "tags")
