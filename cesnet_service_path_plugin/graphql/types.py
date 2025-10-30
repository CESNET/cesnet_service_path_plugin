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
    SegmentFinancialInfo,
    ServicePath,
    ServicePathSegmentMapping,
)

# Import the GraphQL filters
from .filters import (
    SegmentCircuitMappingFilter,
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


@strawberry_django_type(SegmentFinancialInfo)
class SegmentFinancialInfoType(NetBoxObjectType):
    """
    GraphQL type for SegmentFinancialInfo with permission checking.
    Financial data will only be exposed if user has view permission.
    """

    id: auto
    monthly_charge: auto
    charge_currency: auto
    non_recurring_charge: auto
    commitment_period_months: auto
    notes: auto

    # Related segment (simplified reference)
    segment: Annotated["SegmentType", lazy(".types")]

    @field
    def total_commitment_cost(self, info) -> Optional[Decimal]:
        """Calculate total cost over commitment period - only if user has permission"""
        # Permission check happens at the query level, so if we're here, user has access
        return self.total_commitment_cost

    @field
    def total_cost_including_setup(self, info) -> Optional[Decimal]:
        """Total cost including non-recurring charge - only if user has permission"""
        return self.total_cost_including_setup

    @field
    def commitment_end_date(self, info) -> Optional[str]:
        """Calculate the end date of the commitment period - only if user has permission"""
        end_date = self.commitment_end_date
        if end_date:
            return end_date.isoformat()
        return None


@strawberry_django_type(Segment, filters=SegmentFilter)
class SegmentType(NetBoxObjectType):
    id: auto
    name: auto
    network_label: auto
    install_date: auto
    termination_date: auto
    status: auto

    # Segment type fields
    segment_type: auto
    type_specific_data: auto

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
    def financial_info(self, info) -> Optional[Annotated["SegmentFinancialInfoType", lazy(".types")]]:
        """
        Return financial info only if user has permission to view it.
        This mimics the REST API behavior.
        """
        request = info.context.get("request")

        if not request:
            return None

        # Check if user has permission to view financial info
        has_financial_view_perm = request.user.has_perm("cesnet_service_path_plugin.view_segmentfinancialinfo")

        if not has_financial_view_perm:
            return None

        # Try to get financial info if user has permission
        financial_info = getattr(self, "financial_info", None)

        return financial_info if financial_info else None

    @field
    def has_financial_info(self) -> bool:
        """Whether this segment has associated financial info"""
        if hasattr(self, "financial_info") and self.financial_info is not None:
            return True
        return False

    @field
    def has_type_specific_data(self) -> bool:
        """Whether this segment has type-specific data"""
        if hasattr(self, "has_type_specific_data"):
            return self.has_type_specific_data()
        return bool(self.type_specific_data)

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
