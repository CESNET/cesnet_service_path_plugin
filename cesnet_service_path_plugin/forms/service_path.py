from django import forms
from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelForm,
)
from utilities.forms import add_blank_choice
from utilities.forms.fields import CommentField
from utilities.forms.rendering import FieldSet

from cesnet_service_path_plugin.models import ServicePath
from cesnet_service_path_plugin.models.custom_choices import KindChoices, StatusChoices


class ServicePathForm(NetBoxModelForm):
    comments = CommentField(required=False, label="Comments", help_text="Comments")
    status = forms.ChoiceField(
        required=True,
        choices=StatusChoices,
        initial=StatusChoices.ACTIVE,
    )
    kind = forms.ChoiceField(required=True, choices=KindChoices, initial=KindChoices.CORE)

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

    name = forms.CharField(required=False)
    status = forms.ChoiceField(required=False, choices=add_blank_choice(StatusChoices), initial=None)
    kind = forms.ChoiceField(required=False, choices=add_blank_choice(KindChoices), initial=None)

    fieldsets = (
        FieldSet("q", "tag", "filter_id", name="Misc"),
        FieldSet("name", "status", "kind", name="Service Path"),
    )


class ServicePathBulkEditForm(NetBoxModelBulkEditForm):
    status = forms.ChoiceField(
        choices=add_blank_choice(StatusChoices),
        required=False,
        initial="",
    )
    kind = forms.ChoiceField(
        choices=add_blank_choice(KindChoices),
        required=False,
        initial="",
    )
    comments = CommentField()

    model = ServicePath
    fieldsets = (FieldSet("status", "kind", name="Service Path"),)
    nullable_fields = ("comments",)
