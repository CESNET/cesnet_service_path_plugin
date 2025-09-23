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

    # Type-specific field filters - Dark Fiber
    fiber_type: FilterLookup[str] | None = None
    fiber_attenuation_max: Optional[TypeSpecificNumericFilter] = None
    total_loss: Optional[TypeSpecificNumericFilter] = None
    total_length: Optional[TypeSpecificNumericFilter] = None
    number_of_fibers: Optional[TypeSpecificIntegerFilter] = None
    connector_type: FilterLookup[str] | None = None

    # Type-specific field filters - Optical Spectrum
    wavelength: Optional[TypeSpecificNumericFilter] = None
    spectral_slot_width: Optional[TypeSpecificNumericFilter] = None
    itu_grid_position: Optional[TypeSpecificIntegerFilter] = None
    modulation_format: FilterLookup[str] | None = None

    # Type-specific field filters - Ethernet Service
    port_speed: Optional[TypeSpecificIntegerFilter] = None
    vlan_id: Optional[TypeSpecificIntegerFilter] = None
    mtu_size: Optional[TypeSpecificIntegerFilter] = None
    encapsulation_type: FilterLookup[str] | None = None
    interface_type: FilterLookup[str] | None = None

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

    def filter_fiber_type(self, queryset, info):
        if self.fiber_type is None:
            return queryset
        return queryset.filter(type_specific_data__fiber_type=self.fiber_type)

    def filter_connector_type(self, queryset, info):
        if self.connector_type is None:
            return queryset
        return queryset.filter(type_specific_data__connector_type=self.connector_type)

    def filter_modulation_format(self, queryset, info):
        if self.modulation_format is None:
            return queryset
        return queryset.filter(type_specific_data__modulation_format=self.modulation_format)

    def filter_encapsulation_type(self, queryset, info):
        if self.encapsulation_type is None:
            return queryset
        return queryset.filter(type_specific_data__encapsulation_type=self.encapsulation_type)

    def filter_interface_type(self, queryset, info):
        if self.interface_type is None:
            return queryset
        return queryset.filter(type_specific_data__interface_type=self.interface_type)

    def _filter_numeric_field(self, queryset, field_name: str, filter_input: TypeSpecificNumericFilter):
        """Helper method to filter numeric type-specific fields"""
        if filter_input is None:
            return queryset

        conditions = Q(type_specific_data__has_key=field_name)

        if filter_input.exact is not None:
            conditions &= Q(
                pk__in=queryset.extra(
                    where=["(type_specific_data->>%s)::decimal = %s"], params=[field_name, filter_input.exact]
                ).values("pk")
            )

        if filter_input.gt is not None:
            conditions &= Q(
                pk__in=queryset.extra(
                    where=["(type_specific_data->>%s)::decimal > %s"], params=[field_name, filter_input.gt]
                ).values("pk")
            )

        if filter_input.gte is not None:
            conditions &= Q(
                pk__in=queryset.extra(
                    where=["(type_specific_data->>%s)::decimal >= %s"], params=[field_name, filter_input.gte]
                ).values("pk")
            )

        if filter_input.lt is not None:
            conditions &= Q(
                pk__in=queryset.extra(
                    where=["(type_specific_data->>%s)::decimal < %s"], params=[field_name, filter_input.lt]
                ).values("pk")
            )

        if filter_input.lte is not None:
            conditions &= Q(
                pk__in=queryset.extra(
                    where=["(type_specific_data->>%s)::decimal <= %s"], params=[field_name, filter_input.lte]
                ).values("pk")
            )

        if filter_input.range_min is not None and filter_input.range_max is not None:
            conditions &= Q(
                pk__in=queryset.extra(
                    where=["(type_specific_data->>%s)::decimal BETWEEN %s AND %s"],
                    params=[field_name, filter_input.range_min, filter_input.range_max],
                ).values("pk")
            )

        return queryset.filter(conditions)

    def _filter_integer_field(self, queryset, field_name: str, filter_input: TypeSpecificIntegerFilter):
        """Helper method to filter integer type-specific fields"""
        if filter_input is None:
            return queryset

        conditions = Q(type_specific_data__has_key=field_name)

        if filter_input.exact is not None:
            conditions &= Q(
                pk__in=queryset.extra(
                    where=["(type_specific_data->>%s)::integer = %s"], params=[field_name, filter_input.exact]
                ).values("pk")
            )

        if filter_input.gt is not None:
            conditions &= Q(
                pk__in=queryset.extra(
                    where=["(type_specific_data->>%s)::integer > %s"], params=[field_name, filter_input.gt]
                ).values("pk")
            )

        if filter_input.gte is not None:
            conditions &= Q(
                pk__in=queryset.extra(
                    where=["(type_specific_data->>%s)::integer >= %s"], params=[field_name, filter_input.gte]
                ).values("pk")
            )

        if filter_input.lt is not None:
            conditions &= Q(
                pk__in=queryset.extra(
                    where=["(type_specific_data->>%s)::integer < %s"], params=[field_name, filter_input.lt]
                ).values("pk")
            )

        if filter_input.lte is not None:
            conditions &= Q(
                pk__in=queryset.extra(
                    where=["(type_specific_data->>%s)::integer <= %s"], params=[field_name, filter_input.lte]
                ).values("pk")
            )

        if filter_input.range_min is not None and filter_input.range_max is not None:
            conditions &= Q(
                pk__in=queryset.extra(
                    where=["(type_specific_data->>%s)::integer BETWEEN %s AND %s"],
                    params=[field_name, filter_input.range_min, filter_input.range_max],
                ).values("pk")
            )

        return queryset.filter(conditions)

    # Apply filters for numeric fields
    def filter_fiber_attenuation_max(self, queryset, info):
        return self._filter_numeric_field(queryset, "fiber_attenuation_max", self.fiber_attenuation_max)

    def filter_total_loss(self, queryset, info):
        return self._filter_numeric_field(queryset, "total_loss", self.total_loss)

    def filter_total_length(self, queryset, info):
        return self._filter_numeric_field(queryset, "total_length", self.total_length)

    def filter_wavelength(self, queryset, info):
        return self._filter_numeric_field(queryset, "wavelength", self.wavelength)

    def filter_spectral_slot_width(self, queryset, info):
        return self._filter_numeric_field(queryset, "spectral_slot_width", self.spectral_slot_width)

    # Apply filters for integer fields
    def filter_number_of_fibers(self, queryset, info):
        return self._filter_integer_field(queryset, "number_of_fibers", self.number_of_fibers)

    def filter_itu_grid_position(self, queryset, info):
        return self._filter_integer_field(queryset, "itu_grid_position", self.itu_grid_position)

    def filter_port_speed(self, queryset, info):
        return self._filter_integer_field(queryset, "port_speed", self.port_speed)

    def filter_vlan_id(self, queryset, info):
        return self._filter_integer_field(queryset, "vlan_id", self.vlan_id)

    def filter_mtu_size(self, queryset, info):
        return self._filter_integer_field(queryset, "mtu_size", self.mtu_size)


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
