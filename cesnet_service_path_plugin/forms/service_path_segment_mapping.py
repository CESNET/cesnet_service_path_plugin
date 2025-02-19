from django.utils.translation import gettext as _
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms.fields import (
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet

from cesnet_service_path_plugin.models import (
    Segment,
    ServicePath,
    ServicePathSegmentMapping,
)


class ServicePathSegmentMappingFilterForm(NetBoxModelFilterSetForm):
    model = ServicePathSegmentMapping

    tag = TagFilterField(model)

    segment_id = DynamicModelMultipleChoiceField(
        queryset=Segment.objects.all(), required=False, label=_("Segment")
    )
    service_path_id = DynamicModelMultipleChoiceField(
        queryset=ServicePath.objects.all(), required=False, label=_("Service Path")
    )

    fieldsets = (
        FieldSet("q", "tag", "filter_id", name="Misc"),
        FieldSet("segment_id", "service_path_id", name="Basic"),
    )


class ServicePathSegmentMappingForm(NetBoxModelForm):
    segment = DynamicModelChoiceField(
        queryset=Segment.objects.all(), required=True, selector=True
    )
    service_path = DynamicModelChoiceField(
        queryset=ServicePath.objects.all(), required=True, selector=True
    )

    class Meta:
        model = ServicePathSegmentMapping
        fields = ("segment", "service_path")
