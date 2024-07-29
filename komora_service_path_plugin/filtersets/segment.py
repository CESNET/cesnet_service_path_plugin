import django_filters
from extras.filters import TagFilter
from netbox.filtersets import NetBoxModelFilterSet
from komora_service_path_plugin.models import Segment
from dcim.models import Site, Device, Interface, Location
from circuits.models import Provider
from django.db.models import Q


class SegmentFilterSet(NetBoxModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    tag = TagFilter()
    name = django_filters.CharFilter(lookup_expr="icontains")
    network_label = django_filters.CharFilter(lookup_expr="icontains")
    install_date__gte = django_filters.DateTimeFilter(
        field_name='install_date',
        lookup_expr='gte'
    )
    install_date__lte = django_filters.DateTimeFilter(
        field_name='install_date',
        lookup_expr='lte'
    )
    termination_date__gte = django_filters.DateTimeFilter(
        field_name='termination_date',
        lookup_expr='gte'
    )
    termination_date__lte = django_filters.DateTimeFilter(
        field_name='termination_date',
        lookup_expr='lte'
    )
    provider_id = django_filters.ModelMultipleChoiceFilter(
        field_name='provider__id',
        queryset=Provider.objects.all(),
        to_field_name='id',
        label='Provider (ID)',
    )
    provider_segment_id = django_filters.CharFilter(lookup_expr="icontains")
    provider_segment_name = django_filters.CharFilter(lookup_expr="icontains")
    provider_segment_contract = django_filters.CharFilter(
        lookup_expr="icontains")

    site_a_id = django_filters.ModelMultipleChoiceFilter(
        field_name='site_a__id',
        queryset=Site.objects.all(),
        to_field_name='id',
        label='Site A (ID)',
    )
    location_a_id = django_filters.ModelMultipleChoiceFilter(
        field_name='location_a__id',
        queryset=Location.objects.all(),
        to_field_name='id',
        label='Location A (ID)',
    )
    device_a_id = django_filters.ModelMultipleChoiceFilter(
        field_name='device_a__id',
        queryset=Device.objects.all(),
        to_field_name='id',
        label='Device A (ID)',
    )
    port_a_id = django_filters.ModelMultipleChoiceFilter(
        field_name='port_a__id',
        queryset=Interface.objects.all(),
        to_field_name='id',
        label='Port A (ID)',
    )

    site_b_id = django_filters.ModelMultipleChoiceFilter(
        field_name='site_b__id',
        queryset=Site.objects.all(),
        to_field_name='id',
        label='Site B (ID)',
    )
    location_b_id = django_filters.ModelMultipleChoiceFilter(
        field_name='location_b__id',
        queryset=Location.objects.all(),
        to_field_name='id',
        label='Location B (ID)',
    )
    device_b_id = django_filters.ModelMultipleChoiceFilter(
        field_name='device_b__id',
        queryset=Device.objects.all(),
        to_field_name='id',
        label='Device B (ID)',
    )
    port_b_id = django_filters.ModelMultipleChoiceFilter(
        field_name='port_b__id',
        queryset=Interface.objects.all(),
        to_field_name='id',
        label='Port B (ID)',
    )

    class Meta:
        model = Segment
        fields = [
            "id",
            "name",
            "komora_id",
            "network_label",
            "install_date",
            "termination_date",
            "provider",
            "provider_segment_id",
            "provider_segment_name",
            "provider_segment_contract",
            "site_a",
            "location_a",
            "device_a",
            "port_a",
            "site_b",
            "location_b",
            "device_b",
            "port_b",
        ]

    def search(self, queryset, name, value):
        site_a = Q(site_a__name__icontains=value)
        site_b = Q(site_b__name__icontains=value)
        location_a = Q(location_a__name__icontains=value)
        location_b = Q(location_b__name__icontains=value)
        segment_name = Q(name__icontains=value)
        network_label = Q(network_label__icontains=value)
        provider_segment_id = Q(provider_segment_id__icontains=value)

        return queryset.filter(site_a | site_b | location_a | location_b | segment_name | network_label | provider_segment_id)
