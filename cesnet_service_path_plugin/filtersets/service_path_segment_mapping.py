import django_filters
from django.db.models import Q
from extras.filters import TagFilter
from netbox.filtersets import NetBoxModelFilterSet

from cesnet_service_path_plugin.models import (
    Segment,
    ServicePath,
    ServicePathSegmentMapping,
)


class ServicePathSegmentMappingFilterSet(NetBoxModelFilterSet):
    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )
    tag = TagFilter()
    service_path_id = django_filters.ModelMultipleChoiceFilter(
        field_name="service_path__id",
        queryset=ServicePath.objects.all(),
        to_field_name="id",
        label="Service Path (ID)",
    )
    segment_id = django_filters.ModelMultipleChoiceFilter(
        field_name="segment__id",
        queryset=Segment.objects.all(),
        to_field_name="id",
        label="Segment (ID)",
    )

    class Meta:
        model = ServicePathSegmentMapping
        fields = [
            "id",
            "service_path",
            "segment",
        ]

    def search(self, queryset, name, value):
        segment_name = Q(segment__name__icontains=value)
        segment_site_a = Q(segment__site_a__name__icontains=value)
        segment_site_b = Q(segment__site_b__name__icontains=value)
        segment_location_a = Q(segment__location_a__name__icontains=value)
        segment_location_b = Q(segment__location_b__name__icontains=value)

        service_path_name = Q(service_path__name__icontains=value)

        return queryset.filter(
            segment_name
            | segment_site_a
            | segment_site_b
            | segment_location_a
            | segment_location_b
            | service_path_name
        )
