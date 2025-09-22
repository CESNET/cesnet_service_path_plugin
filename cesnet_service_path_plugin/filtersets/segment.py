import logging
import django_filters
from circuits.models import Circuit, Provider
from dcim.models import Location, Site
from django.db.models import Q
from extras.filters import TagFilter
from netbox.filtersets import NetBoxModelFilterSet

from cesnet_service_path_plugin.models import Segment
from cesnet_service_path_plugin.models.custom_choices import StatusChoices
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
    provider_segment_name = django_filters.CharFilter(lookup_expr="icontains")
    provider_segment_contract = django_filters.CharFilter(lookup_expr="icontains")

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

    # Path data filter
    has_path_data = django_filters.MultipleChoiceFilter(
        choices=[
            (True, "Yes"),
            (False, "No"),
        ],
        method="_has_path_data",
        label="Has Path Data",
    )

    # =============================================================================
    # TYPE-SPECIFIC FILTERS
    # =============================================================================

    # Dark Fiber specific filters
    fiber_type = django_filters.MultipleChoiceFilter(
        choices=[
            ("G.652D", "G.652D"),
            ("G.655", "G.655"),
            ("G.657A1", "G.657A1"),
            ("G.657A2", "G.657A2"),
            ("G.652B", "G.652B"),
            ("G.652C", "G.652C"),
            ("G.653", "G.653"),
            ("G.654E", "G.654E"),
        ],
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
        choices=[
            ("LC/APC", "LC/APC"),
            ("LC/UPC", "LC/UPC"),
            ("SC/APC", "SC/APC"),
            ("SC/UPC", "SC/UPC"),
            ("FC/APC", "FC/APC"),
            ("FC/UPC", "FC/UPC"),
            ("ST/UPC", "ST/UPC"),
            ("E2000/APC", "E2000/APC"),
            ("MTP/MPO", "MTP/MPO"),
        ],
        method="_filter_type_specific_choice",
        label="Connector Type",
    )

    # Optical Spectrum specific filters
    wavelength = django_filters.CharFilter(method="_filter_smart_numeric", label="Wavelength (nm)")

    spectral_slot_width = django_filters.CharFilter(method="_filter_smart_numeric", label="Spectral Slot Width (GHz)")

    itu_grid_position = django_filters.CharFilter(method="_filter_smart_numeric", label="ITU Grid Position")

    modulation_format = django_filters.MultipleChoiceFilter(
        choices=[
            ("NRZ", "NRZ"),
            ("PAM4", "PAM4"),
            ("QPSK", "QPSK"),
            ("16QAM", "16QAM"),
            ("64QAM", "64QAM"),
            ("DP-QPSK", "DP-QPSK"),
            ("DP-16QAM", "DP-16QAM"),
        ],
        method="_filter_type_specific_choice",
        label="Modulation Format",
    )

    # Ethernet Service specific filters
    port_speed = django_filters.CharFilter(method="_filter_smart_numeric", label="Port Speed / Bandwidth (Mbps)")

    vlan_id = django_filters.CharFilter(method="_filter_smart_numeric", label="Primary VLAN ID")

    mtu_size = django_filters.CharFilter(method="_filter_smart_numeric", label="MTU Size (bytes)")

    encapsulation_type = django_filters.MultipleChoiceFilter(
        choices=[
            ("Untagged", "Untagged"),
            ("IEEE 802.1Q", "IEEE 802.1Q"),
            ("IEEE 802.1ad (QinQ)", "IEEE 802.1ad (QinQ)"),
            ("IEEE 802.1ah (PBB)", "IEEE 802.1ah (PBB)"),
            ("MPLS", "MPLS"),
            ("MEF E-Line", "MEF E-Line"),
            ("MEF E-LAN", "MEF E-LAN"),
        ],
        method="_filter_type_specific_choice",
        label="Encapsulation Type",
    )

    interface_type = django_filters.MultipleChoiceFilter(
        choices=[
            ("RJ45", "RJ45"),
            ("SFP", "SFP"),
            ("SFP+", "SFP+"),
            ("QSFP+", "QSFP+"),
            ("QSFP28", "QSFP28"),
            ("QSFP56", "QSFP56"),
            ("OSFP", "OSFP"),
            ("CFP", "CFP"),
            ("CFP2", "CFP2"),
            ("CFP4", "CFP4"),
        ],
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
            "provider_segment_name",
            "provider_segment_contract",
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

    def _has_path_data(self, queryset, name, value):
        """
        Filter segments based on whether they have path data or not

        Args:
            value: List of selected values from choices
                   [True] - show only segments with path data
                   [False] - show only segments without path data
                   [True, False] - show all segments (both with and without)
                   [] - show all segments (nothing selected)
        """
        if not value:
            # Nothing selected, show all segments
            return queryset

        # Convert string values to boolean (django-filter sometimes passes strings)
        bool_values = []
        for v in value:
            if v is True or v == "True" or v:
                bool_values.append(True)
            elif v is False or v == "False" or not v:
                bool_values.append(False)

        if True in bool_values and False in bool_values:
            # Both selected, show all segments
            return queryset
        elif True in bool_values:
            # Only "Yes" selected, show segments with path data
            return queryset.filter(path_geometry__isnull=False)
        elif False in bool_values:
            # Only "No" selected, show segments without path data
            return queryset.filter(path_geometry__isnull=True)
        else:
            # Fallback: show all segments
            return queryset

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
        float_fields = ["fiber_attenuation_max", "total_loss", "total_length", "wavelength", "spectral_slot_width"]
        return "float" if field_name in float_fields else "int"

    def _filter_smart_numeric(self, queryset, name, value):
        """
        Smart numeric filter that handles exact, range, and comparison operations
        Uses raw SQL to handle numeric comparisons in JSON fields properly
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

        operation = parsed_value.get("operation")

        try:
            # Base condition: field must exist and not be null
            conditions = Q(type_specific_data__has_key=name)

            if operation == "exact":
                field_value = parsed_value.get("value")
                # Use raw SQL to cast JSON value to numeric for exact comparison
                conditions &= Q(
                    pk__in=queryset.extra(
                        where=["(type_specific_data->>%s)::decimal = %s"], params=[name, field_value]
                    ).values("pk")
                )
                logger.debug(f"🔍 Exact match using SQL CAST: {name} = {field_value}")

            elif operation == "range":
                min_val = parsed_value.get("min")
                max_val = parsed_value.get("max")

                where_clauses = []
                params = []

                if min_val is not None:
                    where_clauses.append("(type_specific_data->>%s)::decimal >= %s")
                    params.extend([name, min_val])

                if max_val is not None:
                    where_clauses.append("(type_specific_data->>%s)::decimal <= %s")
                    params.extend([name, max_val])

                if where_clauses:
                    conditions &= Q(
                        pk__in=queryset.extra(where=[" AND ".join(where_clauses)], params=params).values("pk")
                    )
                logger.debug(f"🔍 Range using SQL CAST: {min_val} <= {name} <= {max_val}")

            elif operation == "gt":
                field_value = parsed_value.get("value")
                conditions &= Q(
                    pk__in=queryset.extra(
                        where=["(type_specific_data->>%s)::decimal > %s"], params=[name, field_value]
                    ).values("pk")
                )
                logger.debug(f"🔍 Greater than using SQL CAST: {name} > {field_value}")

            elif operation == "gte":
                field_value = parsed_value.get("value")
                conditions &= Q(
                    pk__in=queryset.extra(
                        where=["(type_specific_data->>%s)::decimal >= %s"], params=[name, field_value]
                    ).values("pk")
                )
                logger.debug(f"🔍 Greater than or equal using SQL CAST: {name} >= {field_value}")

            elif operation == "lt":
                field_value = parsed_value.get("value")
                conditions &= Q(
                    pk__in=queryset.extra(
                        where=["(type_specific_data->>%s)::decimal < %s"], params=[name, field_value]
                    ).values("pk")
                )
                logger.debug(f"🔍 Less than using SQL CAST: {name} < {field_value}")

            elif operation == "lte":
                field_value = parsed_value.get("value")
                conditions &= Q(
                    pk__in=queryset.extra(
                        where=["(type_specific_data->>%s)::decimal <= %s"], params=[name, field_value]
                    ).values("pk")
                )
                logger.debug(f"🔍 Less than or equal using SQL CAST: {name} <= {field_value}")

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

        # Create OR conditions for each selected value
        q_conditions = Q()
        for val in value:
            # Use JSON field lookup to check if the field exists and has the specified value
            json_lookup = f"type_specific_data__{name}"
            q_conditions |= Q(**{json_lookup: val})

        return queryset.filter(q_conditions)

    def search(self, queryset, name, value):
        site_a = Q(site_a__name__icontains=value)
        site_b = Q(site_b__name__icontains=value)
        location_a = Q(location_a__name__icontains=value)
        location_b = Q(location_b__name__icontains=value)
        segment_name = Q(name__icontains=value)
        network_label = Q(network_label__icontains=value)
        provider_segment_id = Q(provider_segment_id__icontains=value)
        status = Q(status__iexact=value)
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
            | segment_type
        )
