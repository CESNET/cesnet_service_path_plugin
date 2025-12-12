# cesnet_service_path_plugin/graphql/filters.py
from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from django.db.models import Q
from strawberry.types import Info


from netbox.graphql.filter_mixins import NetBoxModelFilterMixin
from strawberry_django import FilterLookup

if TYPE_CHECKING:
    from circuits.graphql.filters import CircuitFilter, ProviderFilter
    from dcim.graphql.filters import LocationFilter, SiteFilter

from cesnet_service_path_plugin.models import (
    Segment,
    SegmentCircuitMapping,
    ContractInfo,
    ServicePath,
    ServicePathSegmentMapping,
)

__all__ = (
    "SegmentFilter",
    "SegmentCircuitMappingFilter",
    "ContractInfoFilter",
    "ServicePathFilter",
    "ServicePathSegmentMappingFilter",
)


@strawberry_django.filter(ContractInfo, lookups=True)
class ContractInfoFilter(NetBoxModelFilterMixin):
    """GraphQL filter for ContractInfo model"""

    # Basic fields
    contract_number: FilterLookup[str] | None = strawberry_django.filter_field()
    contract_type: FilterLookup[str] | None = strawberry_django.filter_field()

    # Financial fields
    charge_currency: FilterLookup[str] | None = strawberry_django.filter_field()
    recurring_charge_period: FilterLookup[str] | None = strawberry_django.filter_field()

    # Date fields
    start_date: FilterLookup[str] | None = strawberry_django.filter_field()
    end_date: FilterLookup[str] | None = strawberry_django.filter_field()

    # Notes
    notes: FilterLookup[str] | None = strawberry_django.filter_field()

    # Related segments
    segments: Annotated["SegmentFilter", strawberry.lazy(".filters")] | None = strawberry_django.filter_field()

    @strawberry_django.filter_field
    def is_active(self, value: bool, prefix: str) -> Q:
        """Filter contracts based on whether they are active (not superseded)"""
        if value:
            # Active contracts: superseded_by is null
            return Q(**{f"{prefix}superseded_by__isnull": True})
        else:
            # Superseded contracts: superseded_by is not null
            return Q(**{f"{prefix}superseded_by__isnull": False})

    @strawberry_django.filter_field
    def has_previous_version(self, value: bool, prefix: str) -> Q:
        """Filter contracts based on whether they have a previous version"""
        if value:
            # Has previous version: previous_version is not null
            return Q(**{f"{prefix}previous_version__isnull": False})
        else:
            # No previous version (v1): previous_version is null
            return Q(**{f"{prefix}previous_version__isnull": True})


@strawberry_django.filter(Segment, lookups=True)
class SegmentFilter(NetBoxModelFilterMixin):
    """GraphQL filter for Segment model"""

    # Basic fields
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    network_label: FilterLookup[str] | None = strawberry_django.filter_field()
    install_date: FilterLookup[str] | None = strawberry_django.filter_field()  # Date fields as string
    termination_date: FilterLookup[str] | None = strawberry_django.filter_field()
    status: FilterLookup[str] | None = strawberry_django.filter_field()
    ownership_type: FilterLookup[str] | None = strawberry_django.filter_field()
    provider_segment_id: FilterLookup[str] | None = strawberry_django.filter_field()
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

    @strawberry_django.filter_field
    def has_contracts(self, value: bool, prefix: str, info: Info) -> Q:
        """Filter segments based on whether they have associated contracts (M:N relationship)"""

        # Check permission first
        if not self._check_contract_permission(info):
            # Return a condition that matches all segments (no filtering)
            # This prevents leaking information about which segments have contract data
            return Q()

        if value:
            # Filter for segments WITH contracts (M:N relationship via contracts field)
            return Q(**{f"{prefix}contracts__isnull": False})
        else:
            # Filter for segments WITHOUT contracts
            # This needs to exclude segments that have any contracts
            return ~Q(**{f"{prefix}contracts__isnull": False})

    def _check_contract_permission(self, info: Info) -> bool:
        """
        Check if the current user has permission to view contract info.
        Returns True if user has permission, False otherwise.
        """
        # Access the request context from GraphQL info
        if not info.context or not hasattr(info.context, "request"):
            return False

        request = info.context.request
        if not request or not hasattr(request, "user"):
            return False

        return request.user.has_perm("cesnet_service_path_plugin.view_contractinfo")

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
            # Has data: at least one of the three models exists
            return (
                Q(**{f"{prefix}dark_fiber_data__isnull": False})
                | Q(**{f"{prefix}optical_spectrum_data__isnull": False})
                | Q(**{f"{prefix}ethernet_service_data__isnull": False})
            )
        else:
            # No data: none of the three models exist
            return (
                Q(**{f"{prefix}dark_fiber_data__isnull": True})
                & Q(**{f"{prefix}optical_spectrum_data__isnull": True})
                & Q(**{f"{prefix}ethernet_service_data__isnull": True})
            )


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
