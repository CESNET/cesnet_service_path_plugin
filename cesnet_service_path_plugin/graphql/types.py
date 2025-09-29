from typing import Annotated, List, Optional

from circuits.graphql.types import CircuitType, ProviderType
from dcim.graphql.types import LocationType, SiteType
from netbox.graphql.types import NetBoxObjectType
from strawberry import auto, lazy, field
from strawberry_django import type as strawberry_django_type
import strawberry

from cesnet_service_path_plugin.models import (
    Segment,
    SegmentCircuitMapping,
    ServicePath,
    ServicePathSegmentMapping,
)

# Import the GraphQL filters
from .filters import (
    SegmentFilter,
    SegmentCircuitMappingFilter,
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
    provider_segment_name: auto
    provider_segment_contract: auto
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
            from cesnet_service_path_plugin.utils import export_segment_paths_as_geojson
            import json

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
