# cesnet_service_path_plugin/graphql/filters.py
from typing import Annotated, TYPE_CHECKING, Optional

import strawberry
import strawberry_django
from strawberry_django import FilterLookup
from django.db.models import Q

from netbox.graphql.filter_mixins import NetBoxModelFilterMixin

if TYPE_CHECKING:
    from circuits.graphql.filters import CircuitFilter, ProviderFilter
    from dcim.graphql.filters import LocationFilter, SiteFilter

from cesnet_service_path_plugin.models import (
    Segment,
    SegmentCircuitMapping,
    ServicePath,
    ServicePathSegmentMapping,
)


__all__ = (
    "SegmentFilter",
    "SegmentCircuitMappingFilter",
    "ServicePathFilter",
    "ServicePathSegmentMappingFilter",
)


@strawberry.input
class TypeSpecificNumericFilter:
    """Input type for filtering type-specific numeric fields"""

    exact: Optional[float] = None
    gt: Optional[float] = None
    gte: Optional[float] = None
    lt: Optional[float] = None
    lte: Optional[float] = None
    range_min: Optional[float] = None
    range_max: Optional[float] = None


@strawberry.input
class TypeSpecificIntegerFilter:
    """Input type for filtering type-specific integer fields"""

    exact: Optional[int] = None
    gt: Optional[int] = None
    gte: Optional[int] = None
    lt: Optional[int] = None
    lte: Optional[int] = None
    range_min: Optional[int] = None
    range_max: Optional[int] = None


@strawberry_django.filter(Segment, lookups=True)
class SegmentFilter(NetBoxModelFilterMixin):
    """GraphQL filter for Segment model"""

    # Basic fields
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    network_label: FilterLookup[str] | None = strawberry_django.filter_field()
    install_date: FilterLookup[str] | None = strawberry_django.filter_field()  # Date fields as string
    termination_date: FilterLookup[str] | None = strawberry_django.filter_field()
    status: FilterLookup[str] | None = strawberry_django.filter_field()
    provider_segment_id: FilterLookup[str] | None = strawberry_django.filter_field()
    provider_segment_name: FilterLookup[str] | None = strawberry_django.filter_field()
    provider_segment_contract: FilterLookup[str] | None = strawberry_django.filter_field()
    comments: FilterLookup[str] | None = strawberry_django.filter_field()

    # Segment type field
    segment_type: FilterLookup[str] | None = strawberry_django.filter_field()

    # Path geometry fields
    path_length_km: FilterLookup[float] | None = strawberry_django.filter_field()
    path_source_format: FilterLookup[str] | None = strawberry_django.filter_field()
    path_notes: FilterLookup[str] | None = strawberry_django.filter_field()

    # Related fields - using lazy imports to avoid circular dependencies
    provider: Annotated["ProviderFilter", strawberry.lazy("circuits.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )

    site_a: Annotated["SiteFilter", strawberry.lazy("dcim.graphql.filters")] | None = strawberry_django.filter_field()

    location_a: Annotated["LocationFilter", strawberry.lazy("dcim.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )

    site_b: Annotated["SiteFilter", strawberry.lazy("dcim.graphql.filters")] | None = strawberry_django.filter_field()

    location_b: Annotated["LocationFilter", strawberry.lazy("dcim.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )

    circuits: Annotated["CircuitFilter", strawberry.lazy("circuits.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )

    # Custom filter for checking if segment has path data
    has_path_data: Optional[bool] = None

    # Custom filter for checking if segment has type-specific data
    has_type_specific_data: Optional[bool] = None

    def filter_has_path_data(self, queryset, info):
        if self.has_path_data is None:
            return queryset
        if self.has_path_data:
            return queryset.filter(path_geometry__isnull=False)
        else:
            return queryset.filter(path_geometry__isnull=True)

    def filter_has_type_specific_data(self, queryset, info):
        if self.has_type_specific_data is None:
            return queryset
        if self.has_type_specific_data:
            return queryset.exclude(type_specific_data={})
        else:
            return queryset.filter(type_specific_data={})


@strawberry_django.filter(ServicePath, lookups=True)
class ServicePathFilter(NetBoxModelFilterMixin):
    """GraphQL filter for ServicePath model"""

    name: FilterLookup[str] | None = strawberry_django.filter_field()
    status: FilterLookup[str] | None = strawberry_django.filter_field()
    kind: FilterLookup[str] | None = strawberry_django.filter_field()
    comments: FilterLookup[str] | None = strawberry_django.filter_field()

    # Related segments
    segments: Annotated["SegmentFilter", strawberry.lazy(".filters")] | None = strawberry_django.filter_field()


@strawberry_django.filter(SegmentCircuitMapping, lookups=True)
class SegmentCircuitMappingFilter(NetBoxModelFilterMixin):
    """GraphQL filter for SegmentCircuitMapping model"""

    segment: Annotated["SegmentFilter", strawberry.lazy(".filters")] | None = strawberry_django.filter_field()

    circuit: Annotated["CircuitFilter", strawberry.lazy("circuits.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(ServicePathSegmentMapping, lookups=True)
class ServicePathSegmentMappingFilter(NetBoxModelFilterMixin):
    """GraphQL filter for ServicePathSegmentMapping model"""

    service_path: Annotated["ServicePathFilter", strawberry.lazy(".filters")] | None = strawberry_django.filter_field()

    segment: Annotated["SegmentFilter", strawberry.lazy(".filters")] | None = strawberry_django.filter_field()
