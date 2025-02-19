from django import forms
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms.fields import CommentField
from utilities.forms.rendering import FieldSet

from cesnet_service_path_plugin.models import ServicePath
from cesnet_service_path_plugin.models.custom_choices import KindChoices, StatusChoices


class ServicePathForm(NetBoxModelForm):
    comments = CommentField(required=False, label="Comments", help_text="Comments")
    status = forms.ChoiceField(
        required=True, choices=StatusChoices, initial=StatusChoices.ACTIVE
    )
    kind = forms.ChoiceField(
        required=True, choices=KindChoices, initial=KindChoices.CORE
    )

    class Meta:
        model = ServicePath
        fields = (
            "name",
            "status",
            "kind",
            "comments",
            "tags",
        )


class ServicePathFilterForm(NetBoxModelFilterSetForm):
    model = ServicePath
    # TODO: make choices configurable (seperate model maybe)

    name = forms.CharField(required=False)
    status = forms.MultipleChoiceField(
        required=False, choices=StatusChoices, initial=None
    )
    kind = forms.MultipleChoiceField(required=False, choices=KindChoices, initial=None)

    fieldsets = (
        FieldSet("q", "tag", "filter_id", name="Misc"),
        FieldSet("name", "status", "kind", name="Service Path"),
    )
