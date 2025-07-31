# 1. First, let's update your types.py to ensure it's importing correctly
# cesnet_service_path_plugin/graphql/types.py

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
    def has_path_data(self) -> bool:
        """Whether this segment has path geometry data"""
        # Make sure this method exists on your model
        if hasattr(self, "has_path_data") and callable(getattr(self, "has_path_data")):
            return self.has_path_data()
        # Fallback: check if path_geometry field has data
        return bool(self.path_geometry)

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

    @field
    def path_segment_count(self) -> int:
        """Number of path segments in the MultiLineString"""
        if hasattr(self, "get_path_segment_count"):
            return self.get_path_segment_count()
        return 0

    @field
    def path_total_points(self) -> int:
        """Total number of coordinate points across all segments"""
        if hasattr(self, "get_total_points"):
            return self.get_total_points()
        return 0


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
