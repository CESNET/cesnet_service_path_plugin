from netbox.forms import NetBoxModelFilterSetForm
from utilities.forms.fields import (DynamicModelMultipleChoiceField,
                                    TagFilterField)
from django.utils.translation import gettext as _
from utilities.forms.rendering import FieldSet


from komora_service_path_plugin.models import Segment, ServicePath
from komora_service_path_plugin.models import ServicePathSegmentMapping


class ServicePathSegmentMappingFilterForm(NetBoxModelFilterSetForm):
    model = ServicePathSegmentMapping

    tag = TagFilterField(model)

    segment_id = DynamicModelMultipleChoiceField(
        queryset=Segment.objects.all(),
        required=False,
        label=_('Segment')
    )
    service_path_id = DynamicModelMultipleChoiceField(
        queryset=ServicePath.objects.all(),
        required=False,
        label=_('Service Path')
    )

    fieldsets = (
        FieldSet("q", "tag", "filter_id", name="Misc"),
        FieldSet("segment_id", "service_path_id", "komora_id", name="Basic"),
    )
