# cesnet_service_path_plugin/models/segment_types.py

from utilities.choices import ChoiceSet


class SegmentTypeChoices(ChoiceSet):
    """Choices for different types of network segments"""

    key = "cesnet_service_path_plugin.choices.segment_type"

    DARK_FIBER = "dark_fiber"
    OPTICAL_SPECTRUM = "optical_spectrum"
    ETHERNET_SERVICE = "ethernet_service"

    CHOICES = [
        (DARK_FIBER, "Dark Fiber", "purple"),
        (OPTICAL_SPECTRUM, "Optical Spectrum", "orange"),
        (ETHERNET_SERVICE, "Ethernet Service", "green"),
    ]


# Type-specific field schemas for validation and forms
SEGMENT_TYPE_SCHEMAS = {
    SegmentTypeChoices.DARK_FIBER: {
        "fiber_type": {
            "type": "multichoice",
            "label": "Fiber Type",
            "choices": ["G.652D", "G.655", "G.657A1", "G.657A2", "G.652B", "G.652C", "G.653", "G.654E"],
            "required": False,
            "help_text": "ITU-T fiber standard designation",
        },
        "fiber_attenuation_max": {
            "type": "decimal",
            "label": "Fiber Attenuation Max (dB/km)",
            "min_value": 0,
            "max_value": 10,
            "max_digits": 8,
            "decimal_places": 4,
            "required": False,
            "help_text": "Maximum attenuation at 1550nm wavelength",
        },
        "total_loss": {
            "type": "decimal",
            "label": "Total Loss (dB)",
            "min_value": 0,
            "max_value": 100,
            "max_digits": 8,
            "decimal_places": 2,
            "required": False,
            "help_text": "End-to-end optical loss including connectors and splices",
        },
        "total_length": {
            "type": "decimal",
            "label": "Total Length (km)",
            "min_value": 0,
            "max_value": 10000,
            "max_digits": 10,
            "decimal_places": 3,
            "required": False,
            "help_text": "Physical length of the fiber cable",
        },
        "number_of_fibers": {
            "type": "integer",
            "label": "Number of Fibers",
            "min_value": 1,
            "max_value": 1000,
            "required": False,
            "help_text": "Total number of fiber strands in the cable",
        },
        "connector_type_side_a": {
            "type": "choice",
            "label": "Connector Type Side A",
            "choices": ["LC/APC", "LC/UPC", "SC/APC", "SC/UPC", "FC/APC", "FC/UPC", "ST/UPC", "E2000/APC", "MTP/MPO"],
            "required": False,
            "help_text": "Optical connector type and polish",
        },
        "connector_type_side_b": {
            "type": "choice",
            "label": "Connector Type Side B",
            "choices": ["LC/APC", "LC/UPC", "SC/APC", "SC/UPC", "FC/APC", "FC/UPC", "ST/UPC", "E2000/APC", "MTP/MPO"],
            "required": False,
            "help_text": "Optical connector type and polish",
        },
    },
    SegmentTypeChoices.OPTICAL_SPECTRUM: {
        "wavelength": {
            "type": "decimal",
            "label": "Wavelength (nm)",
            "min_value": 1260,
            "max_value": 1625,
            "max_digits": 8,
            "decimal_places": 3,
            "required": False,
            "help_text": "Center wavelength in nanometers (C-band: 1530-1565nm, L-band: 1565-1625nm)",
        },
        "spectral_slot_width": {
            "type": "decimal",
            "label": "Spectral Slot Width (GHz)",
            "min_value": 0,
            "max_value": 1000,
            "max_digits": 8,
            "decimal_places": 3,
            "required": False,
            "help_text": "Optical channel bandwidth in GHz",
        },
        "itu_grid_position": {
            "type": "integer",
            "label": "ITU Grid Position",
            "min_value": -100,
            "max_value": 100,
            "required": False,
            "help_text": "ITU-T G.694.1 standard channel number (0 = 193.1 THz)",
        },
        "chromatic_dispersion": {
            "type": "decimal",
            "label": "Chromatic Dispersion (ps/nm)",
            "min_value": -1000,
            "max_value": 1000,
            "max_digits": 8,
            "decimal_places": 3,
            "required": False,
            "help_text": "Chromatic dispersion at the operating wavelength",
        },
        "pmd_tolerance": {
            "type": "decimal",
            "label": "PMD Tolerance (ps)",
            "min_value": 0,
            "max_value": 100,
            "max_digits": 8,
            "decimal_places": 3,
            "required": False,
            "help_text": "Polarization mode dispersion tolerance",
        },
        "modulation_format": {
            "type": "choice",
            "label": "Modulation Format",
            "choices": ["NRZ", "PAM4", "QPSK", "16QAM", "64QAM", "DP-QPSK", "DP-16QAM"],
            "required": False,
            "help_text": "Digital modulation format",
        },
    },
    SegmentTypeChoices.ETHERNET_SERVICE: {
        "port_speed": {
            "type": "integer",
            "label": "Port Speed / Bandwidth (Mbps)",
            "min_value": 1,
            "max_value": 100000,
            "required": False,
            "help_text": "Ethernet port speed or service bandwidth in Mbps",
        },
        "vlan_id": {
            "type": "integer",
            "label": "Primary VLAN ID",
            "min_value": 1,
            "max_value": 4094,
            "required": False,
            "help_text": "Primary VLAN tag (1-4094)",
        },
        "vlan_tags": {
            "type": "string",
            "label": "Additional VLAN Tags",
            "max_length": 255,
            "required": False,
            "help_text": "Additional VLAN tags for QinQ or multiple VLANs (comma-separated)",
        },
        "encapsulation_type": {
            "type": "choice",
            "label": "Encapsulation Type",
            "choices": [
                "Untagged",
                "IEEE 802.1Q",
                "IEEE 802.1ad (QinQ)",
                "IEEE 802.1ah (PBB)",
                "MPLS",
                "MEF E-Line",
                "MEF E-LAN",
            ],
            "required": False,
            "help_text": "Ethernet encapsulation and tagging method",
        },
        "interface_type": {
            "type": "choice",
            "label": "Interface Type",
            "choices": ["RJ45", "SFP", "SFP+", "QSFP+", "QSFP28", "QSFP56", "OSFP", "CFP", "CFP2", "CFP4"],
            "required": False,
            "help_text": "Physical interface form factor",
        },
        "mtu_size": {
            "type": "integer",
            "label": "MTU Size (bytes)",
            "min_value": 64,
            "max_value": 16000,
            "required": False,
            "help_text": "Maximum transmission unit size",
        },
    },
}


def get_segment_type_schema(segment_type):
    """
    Get the schema for a specific segment type

    Args:
        segment_type: One of SegmentTypeChoices values

    Returns:
        dict: Schema definition for the segment type
    """
    return SEGMENT_TYPE_SCHEMAS.get(segment_type, {})


def get_all_segment_types():
    """
    Get all available segment types

    Returns:
        list: List of (value, label) tuples
    """
    return [(choice[0], choice[1]) for choice in SegmentTypeChoices.CHOICES]


def validate_segment_type_data(segment_type, type_data):
    """
    Validate type-specific data against schema

    Args:
        segment_type: The segment type
        type_data: Dictionary of type-specific data

    Returns:
        dict: Dictionary of validation errors (empty if valid)
    """
    schema = get_segment_type_schema(segment_type)
    if not schema:
        return {}

    errors = {}

    for field_name, field_config in schema.items():
        value = type_data.get(field_name)

        # Skip validation if field is empty and not required
        if value is None or value == "":
            if field_config.get("required", False):
                errors[field_name] = "This field is required"
            continue

        # Type-specific validation
        field_type = field_config["type"]

        try:
            if field_type == "decimal":
                decimal_value = float(value)
                min_val = field_config.get("min_value")
                max_val = field_config.get("max_value")

                if min_val is not None and decimal_value < min_val:
                    errors[field_name] = f"Value must be at least {min_val}"
                elif max_val is not None and decimal_value > max_val:
                    errors[field_name] = f"Value must be at most {max_val}"

            elif field_type == "integer":
                int_value = int(value)
                min_val = field_config.get("min_value")
                max_val = field_config.get("max_value")

                if min_val is not None and int_value < min_val:
                    errors[field_name] = f"Value must be at least {min_val}"
                elif max_val is not None and int_value > max_val:
                    errors[field_name] = f"Value must be at most {max_val}"

            elif field_type == "choice":
                choices = field_config.get("choices", [])
                if choices and value not in choices:
                    errors[field_name] = f"Invalid choice. Must be one of: {', '.join(choices)}"

            elif field_type == "string":
                max_length = field_config.get("max_length")
                if max_length and len(str(value)) > max_length:
                    errors[field_name] = f"Value too long. Maximum {max_length} characters."

        except (ValueError, TypeError):
            if field_type == "decimal":
                errors[field_name] = "Invalid decimal value"
            elif field_type == "integer":
                errors[field_name] = "Invalid integer value"
            else:
                errors[field_name] = "Invalid value"

    return errors
