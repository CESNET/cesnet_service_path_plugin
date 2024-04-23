from django import forms
from ipam.models import Prefix
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import CommentField, DynamicModelChoiceField

from . import segment_path


class ServicePathForm(NetBoxModelForm):
    class Meta:
        model = None
        fields = ("name", "tags")
