import json
import logging

from circuits.api.serializers import CircuitSerializer, ProviderSerializer
from dcim.api.serializers import (
    LocationSerializer,
    SiteSerializer,
)
from django.core.exceptions import ValidationError as DjangoValidationError
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers

from cesnet_service_path_plugin.api.serializers.contract_info import (
    ContractInfoSerializer,
)
from cesnet_service_path_plugin.api.serializers.dark_fiber_data_serializer import (
    DarkFiberSegmentDataSerializer,
)
from cesnet_service_path_plugin.api.serializers.optical_spectrum_data_serializer import (
    OpticalSpectrumSegmentDataSerializer,
)
from cesnet_service_path_plugin.api.serializers.ethernet_service_data_serializer import (
    EthernetServiceSegmentDataSerializer,
)
from cesnet_service_path_plugin.models.segment import Segment
from cesnet_service_path_plugin.utils import (
    determine_file_format_from_extension,
    export_segment_paths_as_geojson,
    process_path_data,
)

logger = logging.getLogger(__name__)


class SegmentBaseSerializer(NetBoxModelSerializer):
    """
    Base serializer for Segment with common fields and type-specific data logic.

    This base class provides:
    - Common nested serializers (provider, sites, locations, circuits)
    - Computed field: type_specific_data
    - Method to retrieve type-specific technical data from relational models

    Subclasses:
    - SegmentSerializer: Lightweight serializer for list views
    - SegmentDetailSerializer: Full serializer with geometry data for detail views
    """

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:cesnet_service_path_plugin-api:segment-detail")
    provider = ProviderSerializer(required=True, nested=True)
    site_a = SiteSerializer(required=True, nested=True)
    location_a = LocationSerializer(required=False, nested=True)
    site_b = SiteSerializer(required=True, nested=True)
    location_b = LocationSerializer(required=False, nested=True)
    circuits = CircuitSerializer(required=False, many=True, nested=True)

    # Computed field: type_specific_data (returns data from relational models based on segment_type)
    type_specific_data = serializers.SerializerMethodField(read_only=True)

    contract_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Segment
        # Fields will be defined in subclasses
        fields = []

    def get_type_specific_data(self, obj):
        """
        Return type-specific technical data from relational models based on segment_type.

        Returns structured data from DarkFiberSegmentData, OpticalSpectrumSegmentData,
        or EthernetServiceSegmentData depending on the segment's type.
        """
        if obj.segment_type == 'dark_fiber' and hasattr(obj, 'dark_fiber_data'):
            return DarkFiberSegmentDataSerializer(obj.dark_fiber_data, context=self.context).data
        elif obj.segment_type == 'optical_spectrum' and hasattr(obj, 'optical_spectrum_data'):
            return OpticalSpectrumSegmentDataSerializer(obj.optical_spectrum_data, context=self.context).data
        elif obj.segment_type == 'ethernet_service' and hasattr(obj, 'ethernet_service_data'):
            return EthernetServiceSegmentDataSerializer(obj.ethernet_service_data, context=self.context).data

        return None

    def get_contract_info(self, obj):
        """
        Only include contract info if the user has permission to view it
        """
        request = self.context.get("request")
        if not request:
            return None

        # Check if user has permission to view contract info
        if not request.user.has_perm("cesnet_service_path_plugin.view_contractinfo"):
            return None

        # Fetch and serialize contract info if user has permission
        contract_info = getattr(obj, "contract_info", None)
        if contract_info:
            return ContractInfoSerializer(contract_info, context=self.context).data
        return None


class SegmentSerializer(SegmentBaseSerializer):
    """Default serializer for Segment - lightweight for list views, with file upload support"""

    # Add file upload field
    path_file = serializers.FileField(
        required=False,
        write_only=True,  # Only for input, not included in output
        help_text="Upload a file containing the path geometry. Supported formats: GeoJSON (.geojson, .json), KML (.kml), KMZ (.kmz)",
    )

    # Only include lightweight path info
    has_path_data = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Segment
        fields = (
            "id",
            "url",
            "display",
            "name",
            "segment_type",
            "status",
            "ownership_type",
            "network_label",
            "install_date",
            "termination_date",
            "provider",
            "provider_segment_id",
            "site_a",
            "location_a",
            "site_b",
            "location_b",
            "circuits",
            "type_specific_data",
            # Only basic path info, no heavy geometry
            "path_length_km",
            "path_source_format",
            "path_notes",
            "has_path_data",
            "path_file",
            "contract_info",
            "tags",
        )
        brief_fields = (
            "id",
            "url",
            "display",
            "name",
            "segment_type",
            "status",
            "ownership_type",
            "has_path_data",
            "tags",
        )

    def get_has_path_data(self, obj):
        return obj.has_path_data()

    def update(self, instance, validated_data):
        """Handle file upload during update"""
        path_file = validated_data.pop("path_file", None)

        # Update other fields first
        instance = super().update(instance, validated_data)

        # Process uploaded file if provided
        if path_file:
            try:
                # Process the uploaded file using existing utility functions
                file_format = determine_file_format_from_extension(path_file.name)
                path_geometry = process_path_data(path_file, file_format)

                # Update instance with processed geometry
                instance.path_geometry = path_geometry
                instance.path_source_format = file_format
                # path_length_km will be auto-calculated in the model's save method
                instance.save()

            except DjangoValidationError as e:
                logger.warning(f"Validation Path file error: {str(e)}")
                raise serializers.ValidationError(f"Error processing file '{path_file.name}'")
            except Exception as e:
                logger.error(f"Error processing file '{path_file.name}': {str(e)}")
                raise serializers.ValidationError(f"Error processing file '{path_file.name}'")

        return instance

    def create(self, validated_data):
        """Handle file upload during creation"""
        path_file = validated_data.pop("path_file", None)

        # Create instance without path data first
        instance = super().create(validated_data)

        # Process uploaded file if provided
        if path_file:
            try:
                # Process the uploaded file using existing utility functions
                file_format = determine_file_format_from_extension(path_file.name)
                path_geometry = process_path_data(path_file, file_format)

                # Update instance with processed geometry
                instance.path_geometry = path_geometry
                instance.path_source_format = file_format
                # path_length_km will be auto-calculated in the model's save method
                instance.save()

            except DjangoValidationError as e:
                # Clean up created instance if path processing fails
                instance.delete()
                logger.warning(f"Validation Path file error: {str(e)}")
                raise serializers.ValidationError(f"Error processing file '{path_file.name}'")
            except Exception as e:
                # Clean up created instance if path processing fails
                instance.delete()
                logger.error(f"Error processing file '{path_file.name}': {str(e)}")
                raise serializers.ValidationError(f"Error processing file '{path_file.name}'")

        return instance


class SegmentDetailSerializer(SegmentBaseSerializer):
    """Full serializer with all geometry data for detail views"""

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
            "segment_type",
            "status",
            "ownership_type",
            "network_label",
            "install_date",
            "termination_date",
            "provider",
            "provider_segment_id",
            "site_a",
            "location_a",
            "site_b",
            "location_b",
            "circuits",
            "type_specific_data",
            # All path geometry fields
            "path_geometry_geojson",
            "path_coordinates",
            "path_bounds",
            "path_length_km",
            "path_source_format",
            "path_notes",
            "has_path_data",
            "contract_info",
            "tags",
        )
        brief_fields = (
            "id",
            "url",
            "display",
            "name",
            "segment_type",
            "status",
            "ownership_type",
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
