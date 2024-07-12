from django import forms
from ipam.models import Prefix
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import CommentField

from komora_service_path_plugin.models import ServicePath


class ServicePathForm(NetBoxModelForm):
    comments = CommentField(
        required=False, label="Comments", help_text="Comments")

    fieldsets = (
        (
            "Misc",
            (
                "role",
                "tags",
            ),
        ),
    )

    class Meta:
        model = ServicePath
        fields = (
            "comments",
            "tags",
        )


class ServicePathFilterForm(NetBoxModelFilterSetForm):
    model = ServicePath

    name = forms.CharField(required=False)
    # TODO:
    fieldsets = (
        # (None, ("filter_id", "q")),
        ("Related Objects", ("name", )),
    )
