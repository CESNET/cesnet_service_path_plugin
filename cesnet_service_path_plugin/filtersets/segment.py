import django_filters
from circuits.models import Circuit, Provider
from dcim.models import Device, Interface, Location, Site
from django.db.models import Q
from extras.filters import TagFilter
from netbox.filtersets import NetBoxModelFilterSet

from cesnet_service_path_plugin.models import Segment
from cesnet_service_path_plugin.models.custom_choices import StatusChoices


class SegmentFilterSet(NetBoxModelFilterSet):
    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )
    tag = TagFilter()
    name = django_filters.CharFilter(lookup_expr="icontains")
    network_label = django_filters.CharFilter(lookup_expr="icontains")
    status = django_filters.MultipleChoiceFilter(choices=StatusChoices, null_value=None)

    # @NOTE: Keep commented -> automatically enables date filtering (supports __empty, __lt, __gt, __lte, __gte, __n, ...)
    # install_date = django_filters.DateFilter()
    # termination_date = django_filters.DateFilter()

    provider_id = django_filters.ModelMultipleChoiceFilter(
        field_name="provider__id",
        queryset=Provider.objects.all(),
        to_field_name="id",
        label="Provider (ID)",
    )
    provider_segment_id = django_filters.CharFilter(lookup_expr="icontains")
    provider_segment_name = django_filters.CharFilter(lookup_expr="icontains")
    provider_segment_contract = django_filters.CharFilter(lookup_expr="icontains")

    site_a_id = django_filters.ModelMultipleChoiceFilter(
        field_name="site_a__id",
        queryset=Site.objects.all(),
        to_field_name="id",
        label="Site A (ID)",
    )
    location_a_id = django_filters.ModelMultipleChoiceFilter(
        field_name="location_a__id",
        queryset=Location.objects.all(),
        to_field_name="id",
        label="Location A (ID)",
    )

    site_b_id = django_filters.ModelMultipleChoiceFilter(
        field_name="site_b__id",
        queryset=Site.objects.all(),
        to_field_name="id",
        label="Site B (ID)",
    )
    location_b_id = django_filters.ModelMultipleChoiceFilter(
        field_name="location_b__id",
        queryset=Location.objects.all(),
        to_field_name="id",
        label="Location B (ID)",
    )

    at_any_site = django_filters.ModelMultipleChoiceFilter(
        method="_at_any_site", label="At any Site", queryset=Site.objects.all()
    )

    at_any_location = django_filters.ModelMultipleChoiceFilter(
        method="_at_any_location",
        label="At any Location",
        queryset=Location.objects.all(),
    )

    circuits = django_filters.ModelMultipleChoiceFilter(
        field_name="circuits",
        queryset=Circuit.objects.all(),
        to_field_name="id",
        label="Circuit (ID)",
    )

    class Meta:
        model = Segment
        fields = [
            "id",
            "name",
            "network_label",
            "install_date",
            "termination_date",
            "provider",
            "provider_segment_id",
            "provider_segment_name",
            "provider_segment_contract",
            "site_a",
            "location_a",
            "site_b",
            "location_b",
        ]

    def _at_any_site(self, queryset, name, value):
        if not value:
            return queryset

        site_a = Q(site_a__in=value)
        site_b = Q(site_b__in=value)
        return queryset.filter(site_a | site_b)

    def _at_any_location(self, queryset, name, value):
        if not value:
            return queryset

        location_a = Q(location_a__in=value)
        location_b = Q(location_b__in=value)
        return queryset.filter(location_a | location_b)

    def search(self, queryset, name, value):
        site_a = Q(site_a__name__icontains=value)
        site_b = Q(site_b__name__icontains=value)
        location_a = Q(location_a__name__icontains=value)
        location_b = Q(location_b__name__icontains=value)
        segment_name = Q(name__icontains=value)
        network_label = Q(network_label__icontains=value)
        provider_segment_id = Q(provider_segment_id__icontains=value)
        status = Q(status__iexact=value)

        return queryset.filter(
            site_a
            | site_b
            | location_a
            | location_b
            | segment_name
            | network_label
            | provider_segment_id
            | status
        )
