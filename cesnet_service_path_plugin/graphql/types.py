from typing import Annotated, List

from circuits.graphql.types import CircuitType, ProviderType
from dcim.graphql.types import LocationType, SiteType
from netbox.graphql.types import NetBoxObjectType
from strawberry import auto, lazy
from strawberry_django import type as strawberry_django_type

from cesnet_service_path_plugin.models import (
    Segment,
    SegmentCircuitMapping,
    ServicePath,
    ServicePathSegmentMapping,
)

from .filters import (
    SegmentCircuitMappingFilter,
    SegmentFilter,
    ServicePathFilter,
    ServicePathSegmentMappingFilter,
)


@strawberry_django_type(Segment, filters=SegmentFilter)
class SegmentType(NetBoxObjectType):
    id: auto
    name: auto
    network_label: auto
    install_date: auto
    termination_date: auto
    status: auto
    provider: Annotated["ProviderType", lazy("circuits.graphql.types")] | None
    provider_segment_id: auto
    provider_segment_name: auto
    provider_segment_contract: auto
    site_a: Annotated["SiteType", lazy("dcim.graphql.types")] | None
    location_a: Annotated["LocationType", lazy("dcim.graphql.types")] | None
    site_b: Annotated["SiteType", lazy("dcim.graphql.types")] | None
    location_b: Annotated["LocationType", lazy("dcim.graphql.types")] | None
    comments: auto
    # Circuit
    circuits: List[Annotated["CircuitType", lazy("circuits.graphql.types")]]


@strawberry_django_type(SegmentCircuitMapping, filters=SegmentCircuitMappingFilter)
class SegmentCircuitMappingType(NetBoxObjectType):
    id: auto
    segment: Annotated["SegmentType", lazy(".types")]
    circuit: Annotated["CircuitType", lazy("circuits.graphql.types")]


@strawberry_django_type(ServicePath, filters=ServicePathFilter)
class ServicePathType(NetBoxObjectType):
    id: auto
    name: auto
    status: auto
    kind: auto
    segments: List[Annotated["SegmentType", lazy(".types")]]
    comments: auto


@strawberry_django_type(
    ServicePathSegmentMapping, filters=ServicePathSegmentMappingFilter
)
class ServicePathSegmentMappingType(NetBoxObjectType):
    id: auto
    service_path: Annotated["ServicePathType", lazy(".types")]
    segment: Annotated["SegmentType", lazy(".types")]
