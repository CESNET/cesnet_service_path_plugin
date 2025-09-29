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

    # Custom filter methods with decorator approach
    @strawberry_django.filter_field
    def has_path_data(self, value: bool, prefix: str) -> Q:
        """Filter segments based on whether they have path geometry data"""

        if value:
            # Filter for segments WITH path data
            return Q(**{f"{prefix}path_geometry__isnull": False})
        else:
            # Filter for segments WITHOUT path data
            return Q(**{f"{prefix}path_geometry__isnull": True})

    @strawberry_django.filter_field
    def has_type_specific_data(self, value: bool, prefix: str) -> Q:
        """Filter segments based on whether they have type-specific data"""
        if value:
            # Has type-specific data: JSON field is not empty and not null
            # Return Q object that excludes empty dict and null values
            return ~Q(**{f"{prefix}type_specific_data": {}}) & ~Q(**{f"{prefix}type_specific_data__isnull": True})
        else:
            # No type-specific data: JSON field is empty or null
            return Q(**{f"{prefix}type_specific_data": {}}) | Q(**{f"{prefix}type_specific_data__isnull": True})


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
