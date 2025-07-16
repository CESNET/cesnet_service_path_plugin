import json
from circuits.api.serializers import CircuitSerializer, ProviderSerializer
from dcim.api.serializers import (
    LocationSerializer,
    SiteSerializer,
)
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers

from cesnet_service_path_plugin.models.segment import Segment
from cesnet_service_path_plugin.utils import export_segment_paths_as_geojson


class SegmentSerializer(NetBoxModelSerializer):
    """Default serializer Segment - excludes heavy geometry fields"""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:cesnet_service_path_plugin-api:segment-detail")
    provider = ProviderSerializer(required=True, nested=True)
    site_a = SiteSerializer(required=True, nested=True)
    location_a = LocationSerializer(required=True, nested=True)
    site_b = SiteSerializer(required=True, nested=True)
    location_b = LocationSerializer(required=True, nested=True)
    circuits = CircuitSerializer(required=False, many=True, nested=True)

    # Only include lightweight path info
    has_path_data = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Segment
        fields = (
            "id",
            "url",
            "display",
            "name",
            "status",
            "network_label",
            "install_date",
            "termination_date",
            "provider",
            "provider_segment_id",
            "provider_segment_name",
            "provider_segment_contract",
            "site_a",
            "location_a",
            "site_b",
            "location_b",
            "circuits",
            # Only basic path info, no heavy geometry
            "path_length_km",
            "path_source_format",
            "path_notes",
            "has_path_data",
            "tags",
        )
        brief_fields = (
            "id",
            "url",
            "display",
            "name",
            "status",
            "has_path_data",
            "tags",
        )

    def get_has_path_data(self, obj):
        return obj.has_path_data()


class SegmentListSerializer(NetBoxModelSerializer):
    """Lightweight serializer for list views - excludes heavy geometry fields"""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:cesnet_service_path_plugin-api:segment-detail")
    provider = ProviderSerializer(required=True, nested=True)
    site_a = SiteSerializer(required=True, nested=True)
    location_a = LocationSerializer(required=True, nested=True)
    site_b = SiteSerializer(required=True, nested=True)
    location_b = LocationSerializer(required=True, nested=True)
    circuits = CircuitSerializer(required=False, many=True, nested=True)

    # Only include lightweight path info
    has_path_data = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Segment
        fields = (
            "id",
            "url",
            "display",
            "name",
            "status",
            "network_label",
            "install_date",
            "termination_date",
            "provider",
            "provider_segment_id",
            "provider_segment_name",
            "provider_segment_contract",
            "site_a",
            "location_a",
            "site_b",
            "location_b",
            "circuits",
            # Only basic path info, no heavy geometry
            "path_length_km",
            "path_source_format",
            "path_notes",
            "has_path_data",
            "tags",
        )
        brief_fields = (
            "id",
            "url",
            "display",
            "name",
            "status",
            "has_path_data",
            "tags",
        )

    def get_has_path_data(self, obj):
        return obj.has_path_data()


class SegmentDetailSerializer(NetBoxModelSerializer):
    """Full serializer with all geometry data for detail views"""

    # This is your existing SegmentSerializer - just rename it
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:cesnet_service_path_plugin-api:segment-detail")
    provider = ProviderSerializer(required=True, nested=True)
    site_a = SiteSerializer(required=True, nested=True)
    location_a = LocationSerializer(required=True, nested=True)
    site_b = SiteSerializer(required=True, nested=True)
    location_b = LocationSerializer(required=True, nested=True)
    circuits = CircuitSerializer(required=False, many=True, nested=True)

    # All the heavy geometry fields
    path_geometry_geojson = serializers.SerializerMethodField(read_only=True)
    path_coordinates = serializers.SerializerMethodField(read_only=True)
    path_bounds = serializers.SerializerMethodField(read_only=True)
    has_path_data = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Segment
        fields = (
            "id",
            "url",
            "display",
            "name",
            "status",
            "network_label",
            "install_date",
            "termination_date",
            "provider",
            "provider_segment_id",
            "provider_segment_name",
            "provider_segment_contract",
            "site_a",
            "location_a",
            "site_b",
            "location_b",
            "circuits",
            # All path geometry fields
            "path_geometry_geojson",
            "path_coordinates",
            "path_bounds",
            "path_length_km",
            "path_source_format",
            "path_notes",
            "has_path_data",
            "tags",
        )
        brief_fields = (
            "id",
            "url",
            "display",
            "name",
            "status",
            "has_path_data",
            "tags",
        )

    def get_path_geometry_geojson(self, obj):
        """
        Return path geometry as GeoJSON Feature
        """
        if not obj.has_path_data():
            return None

        try:

            geojson_str = export_segment_paths_as_geojson([obj])
            geojson_data = json.loads(geojson_str)

            # Return just the first (and only) feature, not the entire FeatureCollection
            if geojson_data.get("features"):
                return geojson_data["features"][0]
            return None
        except Exception:
            # Fallback to basic GeoJSON if utility function fails
            return obj.get_path_geojson()

    def get_path_coordinates(self, obj):
        """
        Return path coordinates as list of LineString coordinate arrays
        """
        return obj.get_path_coordinates()

    def get_path_bounds(self, obj):
        """
        Return bounding box of the path geometry [xmin, ymin, xmax, ymax]
        """
        return obj.get_path_bounds()

    def get_has_path_data(self, obj):
        """
        Return boolean indicating if segment has path data
        """
        return obj.has_path_data()

    def validate(self, data):
        # Enforce model validation
        super().validate(data)
        return data
