import django_filters
from django.db.models import Q
from django.utils.translation import gettext as _
from extras.filters import TagFilter
from netbox.filtersets import NetBoxModelFilterSet

from komora_service_path_plugin.forms import ServicePathFilterForm
from komora_service_path_plugin.models import ServicePath


class ServicePathFilterSet(NetBoxModelFilterSet):
    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )
    tag = TagFilter()
    name = django_filters.CharFilter(label=_("Name"))
    state = django_filters.MultipleChoiceFilter(choices=ServicePathFilterForm.STATE_CHOICES, null_value=None)
    kind = django_filters.MultipleChoiceFilter(choices=ServicePathFilterForm.KIND_CHOICES, null_value=None)

    class Meta:
        model = ServicePath
        fields = ["id", "name", "sync_status", "komora_id", "state", "kind", "tag"]

    def search(self, queryset, name, value):
        name = Q(name__icontains=value)
        kind = Q(kind__iexact=value)
        return queryset.filter(name | kind)
