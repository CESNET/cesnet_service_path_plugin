from django import forms
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms.fields import CommentField
from utilities.forms.rendering import FieldSet

from komora_service_path_plugin.models import ServicePath


class ServicePathForm(NetBoxModelForm):
    comments = CommentField(required=False, label="Comments", help_text="Comments")

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
    # TODO: make choices configurable (seperate model maybe)
    STATE_CHOICES = [("", "----")] + [
        (state, state)
        for state in ServicePath.objects.order_by("state")
        .values_list("state", flat=True)
        .distinct()
    ]
    KIND_CHOICES = [("", "----")] + [
        (kind, kind)
        for kind in ServicePath.objects.order_by("kind")
        .values_list("kind", flat=True)
        .distinct()
    ]

    name = forms.CharField(required=False)
    state = forms.ChoiceField(required=False, choices=STATE_CHOICES, initial=None)
    kind = forms.ChoiceField(required=False, choices=KIND_CHOICES, initial=None)

    fieldsets = (
        FieldSet("q", "tag", "filter_id", name="Misc"),
        FieldSet("name", "state", "kind", name="Service Path"),
    )
