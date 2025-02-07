from django import forms
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms.fields import CommentField
from utilities.forms.rendering import FieldSet

from cesnet_service_path_plugin.models import ServicePath, SyncStatusChoices
from cesnet_service_path_plugin.models.service_path import KIND_CHOICES, STATE_CHOICES


class ServicePathForm(NetBoxModelForm):
    comments = CommentField(required=False, label="Comments", help_text="Comments")
    state = forms.ChoiceField(required=True, choices=STATE_CHOICES, initial=None)
    kind = forms.ChoiceField(required=True, choices=KIND_CHOICES, initial=None)

    class Meta:
        model = ServicePath
        fields = (
            "name",
            "state",
            "kind",
            "comments",
            "tags",
        )


class ServicePathFilterForm(NetBoxModelFilterSetForm):
    model = ServicePath
    # TODO: make choices configurable (seperate model maybe)

    name = forms.CharField(required=False)
    sync_status = forms.MultipleChoiceField(
        required=False,
        choices=SyncStatusChoices,
    )
    state = forms.ChoiceField(required=False, choices=STATE_CHOICES, initial=None)
    kind = forms.ChoiceField(required=False, choices=KIND_CHOICES, initial=None)

    fieldsets = (
        FieldSet("q", "tag", "filter_id", "sync_status", name="Misc"),
        FieldSet("name", "state", "kind", name="Service Path"),
    )
