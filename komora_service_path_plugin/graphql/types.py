from typing import Annotated, List
from strawberry import auto, lazy
from strawberry_django import type as strawberry_django_type
from dcim.graphql.types import DeviceType, InterfaceType, LocationType, SiteType
from circuits.graphql.types import CircuitType, ProviderType
from netbox.graphql.types import NetBoxObjectType

from komora_service_path_plugin.models import Segment, ServicePath, ServicePathSegmentMapping, SegmentCircuitMapping
from .filters import SegmentFilter, ServicePathFilter, SegmentCircuitMappingFilter, ServicePathSegmentMappingFilter


@strawberry_django_type(Segment, filters=SegmentFilter)
class SegmentType(NetBoxObjectType):
    id: auto
    name: auto
    network_label: auto
    install_date: auto
    termination_date: auto
    sync_status: auto
    provider: Annotated["ProviderType", lazy("circuits.graphql.types")] | None
    provider_segment_id: auto
    provider_segment_name: auto
    provider_segment_contract: auto
    site_a: Annotated["SiteType", lazy("dcim.graphql.types")] | None
    location_a: Annotated["LocationType", lazy("dcim.graphql.types")] | None
    device_a: Annotated["DeviceType", lazy("dcim.graphql.types")] | None
    port_a: Annotated["InterfaceType", lazy("dcim.graphql.types")] | None
    note_a: auto
    site_b: Annotated["SiteType", lazy("dcim.graphql.types")] | None
    location_b: Annotated["LocationType", lazy("dcim.graphql.types")] | None
    device_b: Annotated["DeviceType", lazy("dcim.graphql.types")] | None
    port_b: Annotated["InterfaceType", lazy("dcim.graphql.types")] | None
    note_b: auto
    imported_data: auto
    komora_id: auto
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
    state: auto
    kind: auto
    sync_status: auto
    segments: List[Annotated["SegmentType", lazy(".types")]]
    imported_data: auto
    komora_id: auto
    comments: auto


@strawberry_django_type(ServicePathSegmentMapping, filters=ServicePathSegmentMappingFilter)
class ServicePathSegmentMappingType(NetBoxObjectType):
    id: auto
    service_path: Annotated["ServicePathType", lazy(".types")]
    segment: Annotated["SegmentType", lazy(".types")]
    index: auto
    imported_data: auto
    komora_id: auto
