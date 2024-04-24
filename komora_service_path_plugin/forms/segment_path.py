from django import forms
from ipam.models import Prefix
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import CommentField, DynamicModelChoiceField

from ..models import SegmentPath


class SegmentPathForm(NetBoxModelForm):
    class Meta:
        model = SegmentPath
        fields = ("name", "tags")
