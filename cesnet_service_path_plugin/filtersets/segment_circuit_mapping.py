import django_filters
from circuits.models import Circuit
from django.db.models import Q
from extras.filters import TagFilter
from cesnet_service_path_plugin.models import Segment, SegmentCircuitMapping
from netbox.filtersets import NetBoxModelFilterSet


class SegmentCircuitMappingFilterSet(NetBoxModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    tag = TagFilter()

    segment_id = django_filters.ModelMultipleChoiceFilter(
        field_name='segment__id',
        queryset=Segment.objects.all(),
        to_field_name='id',
        label='Segment (ID)',
    )
    circuit_id = django_filters.ModelMultipleChoiceFilter(
        field_name='circuit__id',
        queryset=Circuit.objects.all(),
        to_field_name='id',
        label='Circuit (ID)',
    )

    class Meta:
        model = SegmentCircuitMapping
        fields = [
            "id",
            "segment",
            "circuit",
        ]

    def search(self, queryset, name, value):
        segment_name = Q(segment__name__icontains=value)
        segment_site_a = Q(segment__site_a__name__icontains=value)
        segment_site_b = Q(segment__site_b__name__icontains=value)
        segment_location_a = Q(segment__location_a__name__icontains=value)
        segment_location_b = Q(segment__location_b__name__icontains=value)
        circuit_cid = Q(circuit__cid__icontains=value)

        return queryset.filter(segment_name | segment_site_a | segment_site_b | segment_location_a | segment_location_b | circuit_cid)
