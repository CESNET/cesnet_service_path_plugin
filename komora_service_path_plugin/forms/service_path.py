from django import forms
from ipam.models import Prefix
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import CommentField, DynamicModelChoiceField

from ..models import ServicePath


class ServicePathForm(NetBoxModelForm):
    class Meta:
        model = ServicePath
        fields = ("name", "tags")
