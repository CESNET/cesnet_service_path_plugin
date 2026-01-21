import logging

import django_filters
from circuits.models import Circuit, Provider
from dcim.models import Location, Site
from django.db.models import Q
from extras.filters import TagFilter
from netbox.filtersets import NetBoxModelFilterSet
from dcim.choices import InterfaceTypeChoices

from cesnet_service_path_plugin.models import Segment

from cesnet_service_path_plugin.models.custom_choices import (
    StatusChoices,
    OwnershipTypeChoices,
    SingleModeFiberSubtypeChoices,
    ModulationFormatChoices,
    EncapsulationTypeChoices,
)
from dcim.choices import PortTypeChoices
from cesnet_service_path_plugin.models.segment_types import SegmentTypeChoices

logger = logging.getLogger(__name__)


class SegmentFilterSet(NetBoxModelFilterSet):
    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )
    tag = TagFilter()
    name = django_filters.CharFilter(lookup_expr="icontains")
    network_label = django_filters.CharFilter(lookup_expr="icontains")
    status = django_filters.MultipleChoiceFilter(choices=StatusChoices, null_value=None)
    ownership_type = django_filters.MultipleChoiceFilter(choices=OwnershipTypeChoices, null_value=None)

    # Basic segment type filter
    segment_type = django_filters.MultipleChoiceFilter(
        choices=SegmentTypeChoices, null_value=None, label="Segment Type"
    )

    # @NOTE: Keep commented -> automatically enables date filtering (supports __empty, __lt, __gt, __lte, __gte, __n, ...)
    # install_date = django_filters.DateFilter()
    # termination_date = django_filters.DateFilter()

    provider_id = django_filters.ModelMultipleChoiceFilter(
        field_name="provider__id",
        queryset=Provider.objects.all(),
        to_field_name="id",
        label="Provider (ID)",
    )
    provider_segment_id = django_filters.CharFilter(lookup_expr="icontains")

    site_a_id = django_filters.ModelMultipleChoiceFilter(
        field_name="site_a__id",
        queryset=Site.objects.all(),
        to_field_name="id",
        label="Site A (ID)",
    )
    location_a_id = django_filters.ModelMultipleChoiceFilter(
        field_name="location_a__id",
        queryset=Location.objects.all(),
        to_field_name="id",
        label="Location A (ID)",
    )

    site_b_id = django_filters.ModelMultipleChoiceFilter(
        field_name="site_b__id",
        queryset=Site.objects.all(),
        to_field_name="id",
        label="Site B (ID)",
    )
    location_b_id = django_filters.ModelMultipleChoiceFilter(
        field_name="location_b__id",
        queryset=Location.objects.all(),
        to_field_name="id",
        label="Location B (ID)",
    )

    at_any_site = django_filters.ModelMultipleChoiceFilter(
        method="_at_any_site", label="At any Site", queryset=Site.objects.all()
    )

    at_any_location = django_filters.ModelMultipleChoiceFilter(
        method="_at_any_location",
        label="At any Location",
        queryset=Location.objects.all(),
    )

    circuits = django_filters.ModelMultipleChoiceFilter(
        field_name="circuits",
        queryset=Circuit.objects.all(),
        to_field_name="id",
        label="Circuit (ID)",
    )

    # contract info filter
    has_contract_info = django_filters.ChoiceFilter(
        choices=[
            (True, "Yes"),
            (False, "No"),
        ],
        method="_has_contract_info",
        label="Has Contract Info",
    )

    # Path data filter
    has_path_data = django_filters.ChoiceFilter(
        choices=[
            (True, "Yes"),
            (False, "No"),
        ],
        method="_has_path_data",
        label="Has Path Data",
    )

    has_type_specific_data = django_filters.ChoiceFilter(
        choices=[
            ("", "Any"),
            (True, "Yes"),
            (False, "No"),
        ],
        method="_has_type_specific_data",
        label="Has Type-Specific Data",
    )

    # =============================================================================
    # TYPE-SPECIFIC FILTERS
    # =============================================================================

    # Dark Fiber specific filters
    fiber_type = django_filters.MultipleChoiceFilter(
        choices=SingleModeFiberSubtypeChoices,
        method="_filter_type_specific_choice",
        label="Fiber Type",
    )

    fiber_attenuation_max = django_filters.CharFilter(
        method="_filter_smart_numeric", label="Fiber Attenuation Max (dB/km)"
    )

    total_loss = django_filters.CharFilter(method="_filter_smart_numeric", label="Total Loss (dB)")

    total_length = django_filters.CharFilter(method="_filter_smart_numeric", label="Total Length (km)")

    number_of_fibers = django_filters.CharFilter(method="_filter_smart_numeric", label="Number of Fibers")

    connector_type = django_filters.MultipleChoiceFilter(
        choices=PortTypeChoices,
        method="_filter_type_specific_choice",
        label="Connector Type",
    )

    # Optical Spectrum specific filters
    wavelength = django_filters.CharFilter(method="_filter_smart_numeric", label="Wavelength (nm)")

    spectral_slot_width = django_filters.CharFilter(method="_filter_smart_numeric", label="Spectral Slot Width (GHz)")

    itu_grid_position = django_filters.CharFilter(method="_filter_smart_numeric", label="ITU Grid Position")

    modulation_format = django_filters.MultipleChoiceFilter(
        choices=ModulationFormatChoices,
        method="_filter_type_specific_choice",
        label="Modulation Format",
    )

    # Ethernet Service specific filters
    port_speed = django_filters.CharFilter(method="_filter_smart_numeric", label="Port Speed / Bandwidth (Mbps)")

    vlan_id = django_filters.CharFilter(method="_filter_smart_numeric", label="Primary VLAN ID")

    mtu_size = django_filters.CharFilter(method="_filter_smart_numeric", label="MTU Size (bytes)")

    encapsulation_type = django_filters.MultipleChoiceFilter(
        choices=EncapsulationTypeChoices,
        method="_filter_type_specific_choice",
        label="Encapsulation Type",
    )

    interface_type = django_filters.MultipleChoiceFilter(
        choices=InterfaceTypeChoices,
        method="_filter_type_specific_choice",
        label="Interface Type",
    )

    class Meta:
        model = Segment
        fields = [
            "id",
            "name",
            "network_label",
            "segment_type",  # Added segment_type
            "install_date",
            "termination_date",
            "provider",
            "provider_segment_id",
            "site_a",
            "location_a",
            "site_b",
            "location_b",
            "has_path_data",
        ]

    def _at_any_site(self, queryset, name, value):
        if not value:
            return queryset

        site_a = Q(site_a__in=value)
        site_b = Q(site_b__in=value)
        return queryset.filter(site_a | site_b)

    def _at_any_location(self, queryset, name, value):
        if not value:
            return queryset

        location_a = Q(location_a__in=value)
        location_b = Q(location_b__in=value)
        return queryset.filter(location_a | location_b)

    def _has_contract_info(self, queryset, name, value):
        """
        Filter segments based on whether they have associated contract info
        """
        # Check permission first
        if not self._check_contract_permission():
            # Return all segments without applying filter (don't leak info about which have contract data)
            return queryset

        if value in (None, "", []):
            # Nothing selected, show all segments
            return queryset

        has_info = value in [True, "True", "true", "1"]

        if has_info:
            # Only "Yes" selected, show segments with contract info
            return queryset.filter(contracts__isnull=False).distinct()
        else:
            # Only "No" selected, show segments without contract info
            return queryset.filter(contracts__isnull=True)

    def _check_contract_permission(self):
        """
        Check if the current user has permission to view contract info.
        Returns True if user has permission, False otherwise.
        """
        request = self.request
        if not request or not hasattr(request, "user"):
            return False
        return request.user.has_perm("cesnet_service_path_plugin.view_contractinfo")

    def _has_path_data(self, queryset, name, value):
        """
        Filter segments based on whether they have path data or not
        """
        if value in (None, "", []):
            # Nothing selected, show all segments
            return queryset

        has_data = value in [True, "True", "true", "1"]

        if has_data:
            # Only "Yes" selected, show segments with path data
            return queryset.filter(path_geometry__isnull=False)
        else:
            # Only "No" selected, show segments without path data
            return queryset.filter(path_geometry__isnull=True)

    def _has_type_specific_data(self, queryset, name, value):
        """
        Filter segments based on whether they have type-specific data or not.
        Checks if the segment has any of the type-specific models:
        - DarkFiberSegmentData (dark_fiber_data)
        - OpticalSpectrumData (optical_spectrum_data)
        - EthernetServiceData (ethernet_service_data)
        """
        if value in (None, "", []):
            # Nothing selected, show all segments
            return queryset

        has_data = value in [True, "True", "true", "1"]

        if has_data:
            # Only "Yes" selected, show segments with type-specific data
            # Check if segment has any of the three type-specific data models
            return queryset.filter(
                Q(dark_fiber_data__isnull=False)
                | Q(optical_spectrum_data__isnull=False)
                | Q(ethernet_service_data__isnull=False)
            )
        else:
            # Only "No" selected, show segments without type-specific data
            # Must not have any of the three type-specific data models
            return queryset.filter(
                Q(dark_fiber_data__isnull=True)
                & Q(optical_spectrum_data__isnull=True)
                & Q(ethernet_service_data__isnull=True)
            )

    def _parse_smart_numeric_value(self, value, field_type="float"):
        """
        Parse smart numeric input into structured format
        """
        if not value:
            return None

        value = str(value).strip()
        convert_func = float if field_type == "float" else int

        try:
            # Handle different formats
            if value.startswith(">="):
                return {"operation": "gte", "value": convert_func(value[2:].strip())}
            elif value.startswith("<="):
                return {"operation": "lte", "value": convert_func(value[2:].strip())}
            elif value.startswith(">"):
                return {"operation": "gt", "value": convert_func(value[1:].strip())}
            elif value.startswith("<"):
                return {"operation": "lt", "value": convert_func(value[1:].strip())}
            elif value.startswith("="):
                return {"operation": "exact", "value": convert_func(value[1:].strip())}
            elif "-" in value and value.count("-") == 1 and not value.startswith("-"):
                # Range format "10-100"
                min_val, max_val = value.split("-")
                return {
                    "operation": "range",
                    "min": convert_func(min_val.strip()) if min_val.strip() else None,
                    "max": convert_func(max_val.strip()) if max_val.strip() else None,
                }
            else:
                # Exact value (default)
                return {"operation": "exact", "value": convert_func(value)}

        except (ValueError, TypeError) as e:
            logger.error(f"🔍 Error parsing numeric value '{value}': {e}")
            return None

    def _get_field_type(self, field_name):
        """
        Determine the appropriate type for a field based on its name
        """
        float_fields = [
            "fiber_attenuation_max",
            "total_loss",
            "total_length",
            "wavelength",
            "spectral_slot_width",
        ]
        return "float" if field_name in float_fields else "int"

    def _get_field_model_mapping(self, field_name):
        """
        Map field names to their corresponding model relationship path
        Returns tuple of (model_prefix, field_name) or None if not found
        """
        # Dark fiber fields
        dark_fiber_fields = {
            "fiber_attenuation_max": "dark_fiber_data__fiber_attenuation_max",
            "total_loss": "dark_fiber_data__total_loss",
            "total_length": "dark_fiber_data__total_length",
            "number_of_fibers": "dark_fiber_data__number_of_fibers",
        }

        # Optical spectrum fields
        optical_spectrum_fields = {
            "wavelength": "optical_spectrum_data__wavelength",
            "spectral_slot_width": "optical_spectrum_data__spectral_slot_width",
            "itu_grid_position": "optical_spectrum_data__itu_grid_position",
        }

        # Ethernet service fields
        ethernet_service_fields = {
            "port_speed": "ethernet_service_data__port_speed",
            "vlan_id": "ethernet_service_data__vlan_id",
            "mtu_size": "ethernet_service_data__mtu_size",
        }

        if field_name in dark_fiber_fields:
            return dark_fiber_fields[field_name]
        elif field_name in optical_spectrum_fields:
            return optical_spectrum_fields[field_name]
        elif field_name in ethernet_service_fields:
            return ethernet_service_fields[field_name]

        return None

    def _filter_smart_numeric(self, queryset, name, value):
        """
        Smart numeric filter that handles exact, range, and comparison operations
        Uses Django ORM to query type-specific models
        """
        if not value:
            return queryset

        logger.debug(f"🔍 Smart numeric filter called for {name} with raw value: '{value}' (type: {type(value)})")

        # Parse the value if it's still a string
        if isinstance(value, str):
            field_type = self._get_field_type(name)
            parsed_value = self._parse_smart_numeric_value(value, field_type)
            if not parsed_value:
                logger.warning(f"🔍 Could not parse value '{value}' for {name}")
                return queryset
        elif isinstance(value, dict):
            parsed_value = value
        else:
            logger.warning(f"🔍 Unexpected value type for {name}: {type(value)}")
            return queryset

        logger.debug(f"🔍 Parsed value for {name}: {parsed_value}")

        # Get the model field path
        model_field = self._get_field_model_mapping(name)
        if not model_field:
            logger.warning(f"🔍 No model mapping found for field {name}")
            return queryset

        operation = parsed_value.get("operation")

        try:
            conditions = Q()

            if operation == "exact":
                field_value = parsed_value.get("value")
                conditions = Q(**{model_field: field_value})
                logger.debug(f"🔍 Exact match: {model_field} = {field_value}")

            elif operation == "range":
                min_val = parsed_value.get("min")
                max_val = parsed_value.get("max")

                if min_val is not None:
                    conditions &= Q(**{f"{model_field}__gte": min_val})
                if max_val is not None:
                    conditions &= Q(**{f"{model_field}__lte": max_val})

                logger.debug(f"🔍 Range: {min_val} <= {model_field} <= {max_val}")

            elif operation == "gt":
                field_value = parsed_value.get("value")
                conditions = Q(**{f"{model_field}__gt": field_value})
                logger.debug(f"🔍 Greater than: {model_field} > {field_value}")

            elif operation == "gte":
                field_value = parsed_value.get("value")
                conditions = Q(**{f"{model_field}__gte": field_value})
                logger.debug(f"🔍 Greater than or equal: {model_field} >= {field_value}")

            elif operation == "lt":
                field_value = parsed_value.get("value")
                conditions = Q(**{f"{model_field}__lt": field_value})
                logger.debug(f"🔍 Less than: {model_field} < {field_value}")

            elif operation == "lte":
                field_value = parsed_value.get("value")
                conditions = Q(**{f"{model_field}__lte": field_value})
                logger.debug(f"🔍 Less than or equal: {model_field} <= {field_value}")

            else:
                logger.warning(f"🔍 Unknown operation '{operation}' for {name}")
                return queryset

            # Apply the filter
            original_count = queryset.count()
            filtered_queryset = queryset.filter(conditions)
            filtered_count = filtered_queryset.count()

            logger.debug(f"🔍 Filtered from {original_count} to {filtered_count} segments")

            return filtered_queryset

        except Exception as e:
            logger.error(f"🔍 Error in smart numeric filter for {name}: {e}")
            import traceback

            logger.error(f"🔍 Traceback: {traceback.format_exc()}")
            return queryset

    def _get_choice_field_model_mapping(self, field_name):
        """
        Map choice field names to their corresponding model relationship path
        """
        # Dark fiber choice fields
        dark_fiber_fields = {
            "fiber_type": "dark_fiber_data__single_mode_subtype",
            "connector_type": ["dark_fiber_data__connector_type_side_a", "dark_fiber_data__connector_type_side_b"],
        }

        # Optical spectrum choice fields
        optical_spectrum_fields = {
            "modulation_format": "optical_spectrum_data__modulation_format",
        }

        # Ethernet service choice fields
        ethernet_service_fields = {
            "encapsulation_type": "ethernet_service_data__encapsulation_type",
            "interface_type": "ethernet_service_data__interface_type",
        }

        if field_name in dark_fiber_fields:
            return dark_fiber_fields[field_name]
        elif field_name in optical_spectrum_fields:
            return optical_spectrum_fields[field_name]
        elif field_name in ethernet_service_fields:
            return ethernet_service_fields[field_name]

        return None

    def _filter_type_specific_choice(self, queryset, name, value):
        """
        Filter by type-specific choice fields

        Args:
            queryset: Current queryset
            name: Field name (matches the filter name)
            value: List of selected values
        """
        if not value:
            return queryset

        # Get the model field path(s)
        model_fields = self._get_choice_field_model_mapping(name)
        if not model_fields:
            logger.warning(f"🔍 No model mapping found for choice field {name}")
            return queryset

        # Handle both single field and multiple field cases (e.g., connector_type on both sides)
        if isinstance(model_fields, list):
            # Multiple fields - create OR conditions for each field
            q_conditions = Q()
            for model_field in model_fields:
                q_conditions |= Q(**{f"{model_field}__in": value})
            return queryset.filter(q_conditions)
        else:
            # Single field
            return queryset.filter(**{f"{model_fields}__in": value})

    def search(self, queryset, name, value):
        site_a = Q(site_a__name__icontains=value)
        site_b = Q(site_b__name__icontains=value)
        location_a = Q(location_a__name__icontains=value)
        location_b = Q(location_b__name__icontains=value)
        segment_name = Q(name__icontains=value)
        network_label = Q(network_label__icontains=value)
        provider_segment_id = Q(provider_segment_id__icontains=value)
        status = Q(status__iexact=value)
        ownership_type = Q(ownership_type__iexact=value)
        segment_type = Q(segment_type__iexact=value)

        return queryset.filter(
            site_a
            | site_b
            | location_a
            | location_b
            | segment_name
            | network_label
            | provider_segment_id
            | status
            | ownership_type
            | segment_type
        )
