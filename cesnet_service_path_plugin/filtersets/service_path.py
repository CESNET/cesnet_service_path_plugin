import django_filters
from django.db.models import Q
from django.utils.translation import gettext as _
from extras.filters import TagFilter
from netbox.filtersets import NetBoxModelFilterSet

from cesnet_service_path_plugin.models import ServicePath
from cesnet_service_path_plugin.models.custom_choices import StatusChoices
from cesnet_service_path_plugin.models.service_path import KIND_CHOICES


class ServicePathFilterSet(NetBoxModelFilterSet):
    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )
    tag = TagFilter()
    name = django_filters.CharFilter(label=_("Name"))
    status = django_filters.MultipleChoiceFilter(choices=StatusChoices, null_value=None)
    kind = django_filters.MultipleChoiceFilter(choices=KIND_CHOICES, null_value=None)

    class Meta:
        model = ServicePath
        fields = ["id", "name", "status", "kind", "tag"]

    def search(self, queryset, name, value):
        name = Q(name__icontains=value)
        kind = Q(kind__iexact=value)
        return queryset.filter(name | kind)
