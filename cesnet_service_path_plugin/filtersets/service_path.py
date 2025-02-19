import django_filters
from django.db.models import Q
from django.utils.translation import gettext as _
from extras.filters import TagFilter
from netbox.filtersets import NetBoxModelFilterSet

from cesnet_service_path_plugin.models import ServicePath
from cesnet_service_path_plugin.models.custom_choices import KindChoices, StatusChoices


class ServicePathFilterSet(NetBoxModelFilterSet):
    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )
    tag = TagFilter()
    name = django_filters.CharFilter(lookup_expr="icontains")
    status = django_filters.MultipleChoiceFilter(choices=StatusChoices, null_value=None)
    kind = django_filters.MultipleChoiceFilter(choices=KindChoices, null_value=None)
    tag = TagFilter()


    class Meta:
        model = ServicePath
        fields = ["id", "name", "status", "kind", "tag"]

    def search(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value) | Q(comments__icontains=value))
