from django import forms
from ipam.models import Prefix
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import CommentField, DynamicModelChoiceField

from ..models import ServicePathSegmentMapping


class ServicePathSegmentMappingForm(NetBoxModelForm):
    class Meta:
        model = ServicePathSegmentMapping
        fields = ("index", "tags")
