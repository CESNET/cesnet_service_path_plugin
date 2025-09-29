from circuits.models import Circuit
from django.core.exceptions import ValidationError
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.urls import reverse
from django.utils import timezone
from netbox.models import NetBoxModel

from cesnet_service_path_plugin.models.custom_choices import StatusChoices
from cesnet_service_path_plugin.models.segment_types import (
    SegmentTypeChoices,
    SEGMENT_TYPE_SCHEMAS,
    validate_segment_type_data,
)


class Segment(NetBoxModel):
    name = models.CharField(max_length=255)
    network_label = models.CharField(max_length=255, null=True, blank=True)
    install_date = models.DateField(null=True, blank=True)
    termination_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=30,
        choices=StatusChoices,
        default=StatusChoices.ACTIVE,
        blank=False,
        null=False,
    )

    # New segment type field
    segment_type = models.CharField(
        max_length=30,
        choices=SegmentTypeChoices,
        default=SegmentTypeChoices.DARK_FIBER,
        blank=False,
        null=False,
        help_text="Type of network segment",
    )

    # JSON field for type-specific technical parameters
    type_specific_data = models.JSONField(default=dict, blank=True, help_text="Type-specific technical parameters")

    provider = models.ForeignKey(
        "circuits.provider",
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        related_name="+",
    )
    provider_segment_id = models.CharField(max_length=255, null=True, blank=True)
    provider_segment_name = models.CharField(max_length=255, null=True, blank=True)
    provider_segment_contract = models.CharField(max_length=255, null=True, blank=True)

    site_a = models.ForeignKey(
        "dcim.site",
        on_delete=models.PROTECT,
        related_name="+",
        null=False,
        blank=False,
    )
    location_a = models.ForeignKey(
        "dcim.location",
        on_delete=models.PROTECT,
        related_name="+",
        null=False,
        blank=False,
    )

    site_b = models.ForeignKey(
        "dcim.site",
        on_delete=models.PROTECT,
        related_name="+",
        null=False,
        blank=False,
    )
    location_b = models.ForeignKey(
        "dcim.location",
        on_delete=models.PROTECT,
        related_name="+",
        null=False,
        blank=False,
    )

    # GIS fields for storing network segment path
    path_geometry = gis_models.MultiLineStringField(
        srid=4326,  # WGS84 coordinate system
        null=True,
        blank=True,
        help_text="Geographic path of the network segment (supports complex multi-segment paths)",
    )

    # Optional: Store original data format info
    path_source_format = models.CharField(
        max_length=20,
        choices=[
            ("geojson", "GeoJSON"),
            ("kmz", "KMZ"),
            ("kml", "KML"),
            ("manual", "Manual Entry"),
        ],
        null=True,
        blank=True,
        help_text="Source format of the path data",
    )

    # Optional: Store metadata about the path
    path_length_km = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True, help_text="Calculated path length in kilometers"
    )

    path_notes = models.TextField(blank=True, help_text="Additional notes about the path geometry")

    # Circuit
    circuits = models.ManyToManyField(Circuit, through="SegmentCircuitMapping")
    comments = models.TextField(verbose_name="Comments", blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:cesnet_service_path_plugin:segment", args=[self.pk])

    def validate_location_in_site(self, location, site, field_name):
        if location and location.site != site:
            raise ValidationError({field_name: f"Location must be in Site: {site}"})

    def clean(self):
        super().clean()

        self.validate_location_in_site(self.location_a, self.site_a, "location_a")
        self.validate_location_in_site(self.location_b, self.site_b, "location_b")

        # Validate install_date is not greater than termination_date
        if self.install_date and self.termination_date:
            if self.install_date > self.termination_date:
                raise ValidationError(
                    {
                        "install_date": "Install date cannot be later than termination date",
                        "termination_date": "Termination date cannot be earlier than install date",
                    }
                )

        # Validate type-specific data against schema
        if self.segment_type and self.type_specific_data:
            self.validate_type_specific_data()

    def validate_type_specific_data(self):
        """Validate type_specific_data against the schema for this segment type"""
        errors = validate_segment_type_data(self.segment_type, self.type_specific_data)

        if errors:
            raise ValidationError({"type_specific_data": errors})

    def save(self, *args, **kwargs):
        # Auto-calculate path length if geometry is provided
        if self.path_geometry:
            # Transform to a projected coordinate system for accurate length calculation
            # Using Web Mercator (3857) for approximate calculations
            transformed_geom = self.path_geometry.transform(3857, clone=True)
            # MultiLineString always has a length attribute that sums all segments
            self.path_length_km = round(transformed_geom.length / 1000, 3)

        super().save(*args, **kwargs)

    def get_status_color(self):
        return StatusChoices.colors.get(self.status, "gray")

    def get_segment_type_color(self):
        """Get color for segment type badge"""
        return SegmentTypeChoices.colors.get(self.segment_type, "gray")

    def get_type_specific_display(self):
        """Get formatted display of type-specific data for templates"""
        if not self.type_specific_data:
            return {}

        schema = SEGMENT_TYPE_SCHEMAS.get(self.segment_type, {})
        display_data = {}

        for field_name, value in self.type_specific_data.items():
            if value is not None and value != "":
                field_config = schema.get(field_name, {})
                label = field_config.get("label", field_name.replace("_", " ").title())

                # Format the value based on type
                if field_config.get("type") == "decimal" and isinstance(value, (int, float)):
                    # Add units if available in label
                    if "(" in label and ")" in label:
                        # Units are already in the label, just format the number
                        display_data[label] = f"{value:g}"  # Remove trailing zeros
                    else:
                        display_data[label] = f"{value:g}"
                elif field_config.get("type") == "integer":
                    display_data[label] = str(value)
                else:
                    display_data[label] = str(value)

        return display_data

    def get_date_status(self):
        """Returns the date status and color for progress bar"""
        today = timezone.now().date()
        warning_days = 14

        def format_days_message(days, message_type=None):
            if message_type is None:
                message_type = "ago" if days < 0 else "in"
            days = abs(days)
            day_text = "day" if days == 1 else "days"
            return f"{message_type} {days} {day_text}"

        def get_termination_status(days_until):
            if days_until <= 0:
                return {
                    "color": "danger",
                    "message": f"Terminated {format_days_message(days_until)}",
                }
            if days_until <= warning_days:
                return {
                    "color": "warning",
                    "message": f"Terminates {format_days_message(days_until)}",
                }
            return {
                "color": "success",
                "message": f"Active until {self.termination_date.strftime('%Y-%m-%d')}",
            }

        # No dates set
        if not self.install_date and not self.termination_date:
            return None

        # Only termination date set
        if not self.install_date and self.termination_date:
            days_until = (self.termination_date - today).days
            return get_termination_status(days_until)

        # Future installation
        if self.install_date and today < self.install_date:
            days_until = (self.install_date - today).days
            return {
                "color": "info",
                "message": f"Starts {format_days_message(days_until)}",
            }

        # Both dates set
        if self.install_date and self.termination_date:
            total_duration = (self.termination_date - self.install_date).days
            days_until_termination = (self.termination_date - today).days

            # Simple logic for very short durations (2 days or less)
            if total_duration <= 2:
                if days_until_termination <= 0:
                    return {
                        "color": "danger",
                        "message": f"Terminated {format_days_message(days_until_termination)}",
                    }
                return {
                    "color": "warning",
                    "message": f"Terminates {format_days_message(days_until_termination)}",
                }

            # Normal duration segment
            return get_termination_status(days_until_termination)

        # Active without termination date
        return {
            "color": "success",
            "message": "Active",
        }

    # GIS-related helper methods
    def get_path_geojson(self):
        """Return path geometry as GeoJSON"""
        if self.path_geometry:
            return self.path_geometry.geojson
        return None

    def get_path_coordinates(self):
        """Return path coordinates as list of LineString coordinate arrays"""
        if self.path_geometry:
            # MultiLineString always returns list of coordinate arrays for each LineString
            return [list(line.coords) for line in self.path_geometry]
        return None

    def get_path_bounds(self):
        """Return bounding box of the path geometry"""
        if self.path_geometry:
            return self.path_geometry.extent  # Returns (xmin, ymin, xmax, ymax)
        return None

    def has_path_data(self):
        """Check if segment has path geometry data"""
        return self.path_geometry is not None

    def get_path_geometry_type(self):
        """Get the type of path geometry"""
        if self.path_geometry:
            return "MultiLineString"  # Always MultiLineString now
        return None

    def get_path_segment_count(self):
        """Get number of path segments in the MultiLineString"""
        if self.path_geometry:
            return len(self.path_geometry)
        return 0

    def get_total_points(self):
        """Get total number of coordinate points across all segments"""
        if self.path_geometry:
            return sum(len(line.coords) for line in self.path_geometry)
        return 0

    def has_type_specific_data(self):
        """Check if segment has any type-specific data"""
        return bool(self.type_specific_data)
