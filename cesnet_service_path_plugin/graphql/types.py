from typing import Annotated, List, Optional

import strawberry
from circuits.graphql.types import CircuitType, ProviderType
from dcim.graphql.types import LocationType, SiteType
from netbox.graphql.types import NetBoxObjectType
from strawberry import auto, field, lazy
from strawberry_django import type as strawberry_django_type
from decimal import Decimal

from cesnet_service_path_plugin.models import (
    Segment,
    SegmentCircuitMapping,
    ContractInfo,
    ServicePath,
    ServicePathSegmentMapping,
)

# Import the GraphQL filters
from .filters import (
    SegmentCircuitMappingFilter,
    ContractInfoFilter,
    SegmentFilter,
    ServicePathFilter,
    ServicePathSegmentMappingFilter,
)


# Custom scalar types for path geometry data
@strawberry.type
class PathBounds:
    """Bounding box coordinates [xmin, ymin, xmax, ymax]"""

    xmin: float
    ymin: float
    xmax: float
    ymax: float


@strawberry_django_type(ContractInfo, filters=ContractInfoFilter)
class ContractInfoType(NetBoxObjectType):
    """
    GraphQL type for ContractInfo with permission checking.
    Contract data will only be exposed if user has view permission.
    """

    id: auto
    contract_number: auto
    contract_type: auto

    # Financial fields
    recurring_charge: auto
    recurring_charge_period: auto
    number_of_recurring_charges: auto
    charge_currency: auto
    non_recurring_charge: auto

    # Date fields
    start_date: auto
    end_date: auto

    # Notes
    notes: auto

    # Related segments (M:N relationship)
    segments: List[Annotated["SegmentType", lazy(".types")]]

    # Versioning fields (read-only)
    previous_version: Optional[Annotated["ContractInfoType", lazy(".types")]]
    superseded_by: Optional[Annotated["ContractInfoType", lazy(".types")]]

    @field
    def version(self, info) -> int:
        """Calculate version number by counting predecessors"""
        return self.version

    @field
    def is_active(self, info) -> bool:
        """Check if this is the active (not superseded) version"""
        return self.is_active

    @field
    def total_recurring_cost(self, info) -> Optional[Decimal]:
        """Calculate total recurring cost - only if user has permission"""
        # Permission check happens at the query level, so if we're here, user has access
        return self.total_recurring_cost

    @field
    def total_contract_value(self, info) -> Optional[Decimal]:
        """Total contract value including non-recurring charge - only if user has permission"""
        return self.total_contract_value

    @field
    def commitment_end_date(self, info) -> Optional[str]:
        """Calculate commitment end date based on start date and recurring periods"""
        if hasattr(self, "commitment_end_date") and self.commitment_end_date:
            return self.commitment_end_date.isoformat()
        return None


@strawberry_django_type(Segment, filters=SegmentFilter)
class SegmentType(NetBoxObjectType):
    id: auto
    name: auto
    network_label: auto
    install_date: auto
    termination_date: auto
    status: auto
    ownership_type: auto

    # Segment type fields
    segment_type: auto

    provider: Annotated["ProviderType", lazy("circuits.graphql.types")] | None
    provider_segment_id: auto
    site_a: Annotated["SiteType", lazy("dcim.graphql.types")] | None
    location_a: Annotated["LocationType", lazy("dcim.graphql.types")] | None
    site_b: Annotated["SiteType", lazy("dcim.graphql.types")] | None
    location_b: Annotated["LocationType", lazy("dcim.graphql.types")] | None
    comments: auto

    # Path geometry fields
    path_length_km: auto
    path_source_format: auto
    path_notes: auto

    # Circuit relationships
    circuits: List[Annotated["CircuitType", lazy("circuits.graphql.types")]]

    @field
    def contracts(self, info) -> List[Annotated["ContractInfoType", lazy(".types")]]:
        """
        Return contracts only if user has permission to view them.
        This mimics the REST API behavior for M:N relationships.
        """
        request = info.context.get("request")

        if not request:
            return []

        # Check if user has permission to view contract info
        has_contract_view_perm = request.user.has_perm("cesnet_service_path_plugin.view_contractinfo")

        if not has_contract_view_perm:
            return []

        # Return all contracts associated with this segment if user has permission
        if hasattr(self, "contracts"):
            return list(self.contracts.all())
        return []

    @field
    def has_contracts(self) -> bool:
        """Whether this segment has associated contracts"""
        if hasattr(self, "contracts"):
            return self.contracts.exists()
        return False

    @field
    def type_specific_data(self) -> Optional[strawberry.scalars.JSON]:
        """Type-specific technical data from relational models (DarkFiberSegmentData, OpticalSpectrumSegmentData, or EthernetServiceSegmentData)"""
        # Import serializers to get the data in the same format as REST API
        from cesnet_service_path_plugin.api.serializers.dark_fiber_data_serializer import (
            DarkFiberSegmentDataSerializer,
        )
        from cesnet_service_path_plugin.api.serializers.optical_spectrum_data_serializer import (
            OpticalSpectrumSegmentDataSerializer,
        )
        from cesnet_service_path_plugin.api.serializers.ethernet_service_data_serializer import (
            EthernetServiceSegmentDataSerializer,
        )

        if self.segment_type == "dark_fiber" and hasattr(self, "dark_fiber_data"):
            return DarkFiberSegmentDataSerializer(self.dark_fiber_data).data
        elif self.segment_type == "optical_spectrum" and hasattr(self, "optical_spectrum_data"):
            return OpticalSpectrumSegmentDataSerializer(self.optical_spectrum_data).data
        elif self.segment_type == "ethernet_service" and hasattr(self, "ethernet_service_data"):
            return EthernetServiceSegmentDataSerializer(self.ethernet_service_data).data
        return None

    @field
    def has_type_specific_data(self) -> bool:
        """Whether this segment has type-specific data"""
        return (
            hasattr(self, "dark_fiber_data")
            or hasattr(self, "optical_spectrum_data")
            or hasattr(self, "ethernet_service_data")
        )

    @field
    def has_path_data(self) -> bool:
        """Whether this segment has path geometry data"""
        if hasattr(self, "has_path_data") and callable(getattr(self, "has_path_data")):
            return self.has_path_data()
        return bool(self.path_geometry)

    @field
    def segment_type_display(self) -> Optional[str]:
        """Display name for segment type"""
        if hasattr(self, "get_segment_type_display"):
            return self.get_segment_type_display()
        return None

    @field
    def path_geometry_geojson(self) -> Optional[strawberry.scalars.JSON]:
        """Path geometry as GeoJSON Feature"""
        if not self.has_path_data:
            return None

        try:
            # Check if the utility function exists
            import json

            from cesnet_service_path_plugin.utils import export_segment_paths_as_geojson

            geojson_str = export_segment_paths_as_geojson([self])
            geojson_data = json.loads(geojson_str)

            # Return just the first (and only) feature
            if geojson_data.get("features"):
                return geojson_data["features"][0]
            return None
        except (ImportError, AttributeError):
            # Fallback if utility function doesn't exist
            return None
        except Exception:
            # Fallback to basic GeoJSON if available
            if hasattr(self, "get_path_geojson"):
                geojson_str = self.get_path_geojson()
                if geojson_str:
                    import json

                    return json.loads(geojson_str)
            return None

    @field
    def path_coordinates(self) -> Optional[List[List[List[float]]]]:
        """Path coordinates as nested lists [[[lon, lat], [lon, lat]...]]"""
        if hasattr(self, "get_path_coordinates"):
            return self.get_path_coordinates()
        return None

    @field
    def path_bounds(self) -> Optional[PathBounds]:
        """Bounding box of the path geometry"""
        if hasattr(self, "get_path_bounds"):
            bounds = self.get_path_bounds()
            if bounds and len(bounds) >= 4:
                return PathBounds(xmin=bounds[0], ymin=bounds[1], xmax=bounds[2], ymax=bounds[3])
        return None


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


@strawberry_django_type(ServicePathSegmentMapping, filters=ServicePathSegmentMappingFilter)
class ServicePathSegmentMappingType(NetBoxObjectType):
    id: auto
    service_path: Annotated["ServicePathType", lazy(".types")]
    segment: Annotated["SegmentType", lazy(".types")]
