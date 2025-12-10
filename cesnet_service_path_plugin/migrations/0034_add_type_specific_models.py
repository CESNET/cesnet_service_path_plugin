# Generated manually - Type-specific data models migration
#
# This migration creates new models for type-specific segment data:
# - DarkFiberSegmentData
# - OpticalSpectrumSegmentData
# - EthernetServiceSegmentData
#
# It includes data migration from JSON (type_specific_data) to proper DB models.
# The JSON field is NOT removed in this migration - that will be done later.

import django.core.validators
import django.db.models.deletion
import netbox.models.deletion
import taggit.managers
import utilities.json
from decimal import Decimal
from django.db import migrations, models


def migrate_json_to_models_forward(apps, schema_editor):
    """
    Migrate type-specific data from JSON field to proper models.
    Creates appropriate type-specific model instances based on segment_type.
    """
    Segment = apps.get_model("cesnet_service_path_plugin", "Segment")
    DarkFiberSegmentData = apps.get_model("cesnet_service_path_plugin", "DarkFiberSegmentData")
    OpticalSpectrumSegmentData = apps.get_model("cesnet_service_path_plugin", "OpticalSpectrumSegmentData")
    EthernetServiceSegmentData = apps.get_model("cesnet_service_path_plugin", "EthernetServiceSegmentData")

    # Track migration statistics
    stats = {
        "dark_fiber": 0,
        "optical_spectrum": 0,
        "ethernet_service": 0,
        "errors": [],
    }

    for segment in Segment.objects.all():
        if not segment.type_specific_data:
            # No data to migrate
            continue

        try:
            if segment.segment_type == "dark_fiber":
                # Migrate Dark Fiber data
                json_data = segment.type_specific_data

                # Handle fiber_type - was multichoice (list) in JSON
                fiber_type_raw = json_data.get("fiber_type")
                # Note: The new model doesn't have a direct fiber_type list field
                # Instead we have fiber_mode and subtypes
                # For now, we'll skip fiber_type as it's being replaced by the new structure

                DarkFiberSegmentData.objects.create(
                    segment=segment,
                    # New fields - will be empty initially (can be filled manually later)
                    fiber_mode="",
                    single_mode_subtype="",
                    multimode_subtype="",
                    jacket_type="",
                    # Existing fields from JSON
                    fiber_attenuation_max=json_data.get("fiber_attenuation_max"),
                    total_loss=json_data.get("total_loss"),
                    total_length=json_data.get("total_length"),
                    number_of_fibers=json_data.get("number_of_fibers"),
                    connector_type_side_a=_map_connector_type(json_data.get("connector_type_side_a")),
                    connector_type_side_b=_map_connector_type(json_data.get("connector_type_side_b")),
                )
                stats["dark_fiber"] += 1

            elif segment.segment_type == "optical_spectrum":
                # Migrate Optical Spectrum data
                json_data = segment.type_specific_data

                OpticalSpectrumSegmentData.objects.create(
                    segment=segment,
                    wavelength=json_data.get("wavelength"),
                    spectral_slot_width=json_data.get("spectral_slot_width"),
                    itu_grid_position=json_data.get("itu_grid_position"),
                    chromatic_dispersion=json_data.get("chromatic_dispersion"),
                    pmd_tolerance=json_data.get("pmd_tolerance"),
                    modulation_format=_map_modulation_format(json_data.get("modulation_format")),
                )
                stats["optical_spectrum"] += 1

            elif segment.segment_type == "ethernet_service":
                # Migrate Ethernet Service data
                json_data = segment.type_specific_data

                EthernetServiceSegmentData.objects.create(
                    segment=segment,
                    port_speed=json_data.get("port_speed"),
                    vlan_id=json_data.get("vlan_id"),
                    vlan_tags=json_data.get("vlan_tags", ""),
                    encapsulation_type=_map_encapsulation_type(json_data.get("encapsulation_type")),
                    interface_type=_map_interface_type(json_data.get("interface_type")),
                    mtu_size=json_data.get("mtu_size"),
                )
                stats["ethernet_service"] += 1

        except Exception as e:
            error_msg = f"Error migrating segment {segment.pk} ({segment.name}): {str(e)}"
            stats["errors"].append(error_msg)
            print(f"  ⚠️  {error_msg}")

    # Print migration summary
    print(f"\n✅ Migration completed:")
    print(f"  - Dark Fiber segments: {stats['dark_fiber']}")
    print(f"  - Optical Spectrum segments: {stats['optical_spectrum']}")
    print(f"  - Ethernet Service segments: {stats['ethernet_service']}")
    if stats["errors"]:
        print(f"  ⚠️  Errors: {len(stats['errors'])}")
        for error in stats["errors"][:10]:  # Show first 10 errors
            print(f"    {error}")


def _map_connector_type(old_value):
    """Map old connector type values to new choice keys"""
    if not old_value:
        return ""

    # Old format was like "LC/APC", new format is "lc_apc"
    mapping = {
        "LC/APC": "lc_apc",
        "LC/UPC": "lc_upc",
        "SC/APC": "sc_apc",
        "SC/UPC": "sc_upc",
        "FC/APC": "fc_apc",
        "FC/UPC": "fc_upc",
        "ST/UPC": "st_upc",
        "E2000/APC": "e2000_apc",
        "MTP/MPO": "mtp_mpo",
    }
    return mapping.get(old_value, "")


def _map_modulation_format(old_value):
    """Map old modulation format values to new choice keys"""
    if not old_value:
        return ""

    # Old format was like "NRZ", new format is lowercase "nrz"
    mapping = {
        "NRZ": "nrz",
        "PAM4": "pam4",
        "QPSK": "qpsk",
        "16QAM": "16qam",
        "64QAM": "64qam",
        "DP-QPSK": "dp_qpsk",
        "DP-16QAM": "dp_16qam",
    }
    return mapping.get(old_value, old_value.lower() if old_value else "")


def _map_encapsulation_type(old_value):
    """Map old encapsulation type values to new choice keys"""
    if not old_value:
        return ""

    mapping = {
        "Untagged": "untagged",
        "IEEE 802.1Q": "dot1q",
        "IEEE 802.1ad (QinQ)": "dot1ad",
        "IEEE 802.1ah (PBB)": "dot1ah",
        "MPLS": "mpls",
        "MEF E-Line": "mef_e_line",
        "MEF E-LAN": "mef_e_lan",
    }
    return mapping.get(old_value, "")


def _map_interface_type(old_value):
    """Map old interface type values to new choice keys"""
    if not old_value:
        return ""

    mapping = {
        "RJ45": "rj45",
        "SFP": "sfp",
        "SFP+": "sfp_plus",
        "QSFP+": "qsfp_plus",
        "QSFP28": "qsfp28",
        "QSFP56": "qsfp56",
        "OSFP": "osfp",
        "CFP": "cfp",
        "CFP2": "cfp2",
        "CFP4": "cfp4",
    }
    return mapping.get(old_value, "")


def migrate_json_to_models_reverse(apps, schema_editor):
    """
    Reverse migration: Copy data from models back to JSON field.
    This allows rollback if needed.
    """
    Segment = apps.get_model("cesnet_service_path_plugin", "Segment")
    DarkFiberSegmentData = apps.get_model("cesnet_service_path_plugin", "DarkFiberSegmentData")
    OpticalSpectrumSegmentData = apps.get_model("cesnet_service_path_plugin", "OpticalSpectrumSegmentData")
    EthernetServiceSegmentData = apps.get_model("cesnet_service_path_plugin", "EthernetServiceSegmentData")

    # Reverse migrate Dark Fiber
    for df_data in DarkFiberSegmentData.objects.all():
        segment = df_data.segment
        segment.type_specific_data = {
            "fiber_attenuation_max": float(df_data.fiber_attenuation_max)
            if df_data.fiber_attenuation_max
            else None,
            "total_loss": float(df_data.total_loss) if df_data.total_loss else None,
            "total_length": float(df_data.total_length) if df_data.total_length else None,
            "number_of_fibers": df_data.number_of_fibers,
            "connector_type_side_a": _reverse_map_connector_type(df_data.connector_type_side_a),
            "connector_type_side_b": _reverse_map_connector_type(df_data.connector_type_side_b),
        }
        # Remove None values
        segment.type_specific_data = {k: v for k, v in segment.type_specific_data.items() if v is not None}
        segment.save()

    # Reverse migrate Optical Spectrum
    for os_data in OpticalSpectrumSegmentData.objects.all():
        segment = os_data.segment
        segment.type_specific_data = {
            "wavelength": float(os_data.wavelength) if os_data.wavelength else None,
            "spectral_slot_width": float(os_data.spectral_slot_width) if os_data.spectral_slot_width else None,
            "itu_grid_position": os_data.itu_grid_position,
            "chromatic_dispersion": float(os_data.chromatic_dispersion) if os_data.chromatic_dispersion else None,
            "pmd_tolerance": float(os_data.pmd_tolerance) if os_data.pmd_tolerance else None,
            "modulation_format": _reverse_map_modulation_format(os_data.modulation_format),
        }
        segment.type_specific_data = {k: v for k, v in segment.type_specific_data.items() if v is not None}
        segment.save()

    # Reverse migrate Ethernet Service
    for es_data in EthernetServiceSegmentData.objects.all():
        segment = es_data.segment
        segment.type_specific_data = {
            "port_speed": es_data.port_speed,
            "vlan_id": es_data.vlan_id,
            "vlan_tags": es_data.vlan_tags,
            "encapsulation_type": _reverse_map_encapsulation_type(es_data.encapsulation_type),
            "interface_type": _reverse_map_interface_type(es_data.interface_type),
            "mtu_size": es_data.mtu_size,
        }
        segment.type_specific_data = {k: v for k, v in segment.type_specific_data.items() if v is not None}
        segment.save()


def _reverse_map_connector_type(new_value):
    """Reverse map connector type from new choice keys to old display values"""
    if not new_value:
        return None
    mapping = {
        "lc_apc": "LC/APC",
        "lc_upc": "LC/UPC",
        "sc_apc": "SC/APC",
        "sc_upc": "SC/UPC",
        "fc_apc": "FC/APC",
        "fc_upc": "FC/UPC",
        "st_upc": "ST/UPC",
        "e2000_apc": "E2000/APC",
        "mtp_mpo": "MTP/MPO",
    }
    return mapping.get(new_value, new_value)


def _reverse_map_modulation_format(new_value):
    """Reverse map modulation format"""
    if not new_value:
        return None
    mapping = {
        "nrz": "NRZ",
        "pam4": "PAM4",
        "qpsk": "QPSK",
        "16qam": "16QAM",
        "64qam": "64QAM",
        "dp_qpsk": "DP-QPSK",
        "dp_16qam": "DP-16QAM",
    }
    return mapping.get(new_value, new_value.upper())


def _reverse_map_encapsulation_type(new_value):
    """Reverse map encapsulation type"""
    if not new_value:
        return None
    mapping = {
        "untagged": "Untagged",
        "dot1q": "IEEE 802.1Q",
        "dot1ad": "IEEE 802.1ad (QinQ)",
        "dot1ah": "IEEE 802.1ah (PBB)",
        "mpls": "MPLS",
        "mef_e_line": "MEF E-Line",
        "mef_e_lan": "MEF E-LAN",
    }
    return mapping.get(new_value, new_value)


def _reverse_map_interface_type(new_value):
    """Reverse map interface type"""
    if not new_value:
        return None
    mapping = {
        "rj45": "RJ45",
        "sfp": "SFP",
        "sfp_plus": "SFP+",
        "qsfp_plus": "QSFP+",
        "qsfp28": "QSFP28",
        "qsfp56": "QSFP56",
        "osfp": "OSFP",
        "cfp": "CFP",
        "cfp2": "CFP2",
        "cfp4": "CFP4",
    }
    return mapping.get(new_value, new_value.upper())


class Migration(migrations.Migration):

    dependencies = [
        ("cesnet_service_path_plugin", "0033_contractinfo_contractsegmentmapping_and_more"),
        ("extras", "0133_make_cf_minmax_decimal"),
    ]

    operations = [
        # ====================================================================
        # Create DarkFiberSegmentData Model
        # ====================================================================
        migrations.CreateModel(
            name="DarkFiberSegmentData",
            fields=[
                (
                    "segment",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="dark_fiber_data",
                        serialize=False,
                        to="cesnet_service_path_plugin.segment",
                        help_text="Associated segment (1:1 relationship)",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                (
                    "fiber_mode",
                    models.CharField(
                        blank=True,
                        max_length=20,
                        help_text="Fiber mode: Single-mode (SMF) or Multimode (MMF)",
                    ),
                ),
                (
                    "single_mode_subtype",
                    models.CharField(
                        blank=True,
                        max_length=20,
                        help_text="ITU-T single-mode fiber standard (G.652-G.657) - only for single-mode fibers",
                    ),
                ),
                (
                    "multimode_subtype",
                    models.CharField(
                        blank=True,
                        max_length=20,
                        help_text="ISO/IEC multimode fiber standard (OM1-OM5) - only for multimode fibers",
                    ),
                ),
                (
                    "jacket_type",
                    models.CharField(
                        blank=True,
                        max_length=30,
                        help_text="Cable jacket/construction type (indoor/outdoor, armored, loose tube, etc.)",
                    ),
                ),
                (
                    "fiber_attenuation_max",
                    models.DecimalField(
                        blank=True,
                        decimal_places=4,
                        max_digits=8,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(10),
                        ],
                        help_text="Maximum attenuation at 1550nm wavelength (dB/km)",
                    ),
                ),
                (
                    "total_loss",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=8,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(100),
                        ],
                        help_text="End-to-end optical loss including connectors and splices (dB)",
                    ),
                ),
                (
                    "total_length",
                    models.DecimalField(
                        blank=True,
                        decimal_places=3,
                        max_digits=10,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(10000),
                        ],
                        help_text="Physical length of the fiber cable (km)",
                    ),
                ),
                (
                    "number_of_fibers",
                    models.PositiveIntegerField(
                        blank=True,
                        null=True,
                        validators=[django.core.validators.MaxValueValidator(1000)],
                        help_text="Total number of fiber strands in the cable",
                    ),
                ),
                (
                    "connector_type_side_a",
                    models.CharField(
                        blank=True,
                        max_length=30,
                        help_text="Optical connector type and polish (Side A)",
                    ),
                ),
                (
                    "connector_type_side_b",
                    models.CharField(
                        blank=True,
                        max_length=30,
                        help_text="Optical connector type and polish (Side B)",
                    ),
                ),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "verbose_name": "Dark Fiber Technical Data",
                "verbose_name_plural": "Dark Fiber Technical Data",
                "ordering": ("segment",),
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
        # ====================================================================
        # Create OpticalSpectrumSegmentData Model
        # ====================================================================
        migrations.CreateModel(
            name="OpticalSpectrumSegmentData",
            fields=[
                (
                    "segment",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="optical_spectrum_data",
                        serialize=False,
                        to="cesnet_service_path_plugin.segment",
                        help_text="Associated segment (1:1 relationship)",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                (
                    "wavelength",
                    models.DecimalField(
                        blank=True,
                        decimal_places=3,
                        max_digits=8,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(1260),
                            django.core.validators.MaxValueValidator(1625),
                        ],
                        help_text="Center wavelength in nanometers (C-band: 1530-1565nm, L-band: 1565-1625nm)",
                    ),
                ),
                (
                    "spectral_slot_width",
                    models.DecimalField(
                        blank=True,
                        decimal_places=3,
                        max_digits=8,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(1000),
                        ],
                        help_text="Optical channel bandwidth (GHz)",
                    ),
                ),
                (
                    "itu_grid_position",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(-100),
                            django.core.validators.MaxValueValidator(100),
                        ],
                        help_text="ITU-T G.694.1 standard channel number (0 = 193.1 THz)",
                    ),
                ),
                (
                    "chromatic_dispersion",
                    models.DecimalField(
                        blank=True,
                        decimal_places=3,
                        max_digits=8,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(-1000),
                            django.core.validators.MaxValueValidator(1000),
                        ],
                        help_text="Chromatic dispersion at the operating wavelength (ps/nm)",
                    ),
                ),
                (
                    "pmd_tolerance",
                    models.DecimalField(
                        blank=True,
                        decimal_places=3,
                        max_digits=8,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(100),
                        ],
                        help_text="Polarization mode dispersion tolerance (ps)",
                    ),
                ),
                (
                    "modulation_format",
                    models.CharField(
                        blank=True,
                        max_length=30,
                        help_text="Digital modulation format",
                    ),
                ),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "verbose_name": "Optical Spectrum Technical Data",
                "verbose_name_plural": "Optical Spectrum Technical Data",
                "ordering": ("segment",),
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
        # ====================================================================
        # Create EthernetServiceSegmentData Model
        # ====================================================================
        migrations.CreateModel(
            name="EthernetServiceSegmentData",
            fields=[
                (
                    "segment",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="ethernet_service_data",
                        serialize=False,
                        to="cesnet_service_path_plugin.segment",
                        help_text="Associated segment (1:1 relationship)",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                (
                    "port_speed",
                    models.PositiveIntegerField(
                        blank=True,
                        null=True,
                        validators=[django.core.validators.MaxValueValidator(100000)],
                        help_text="Ethernet port speed or service bandwidth (Mbps)",
                    ),
                ),
                (
                    "vlan_id",
                    models.PositiveIntegerField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(4094),
                        ],
                        help_text="Primary VLAN tag (1-4094)",
                    ),
                ),
                (
                    "vlan_tags",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        help_text="Additional VLAN tags for QinQ or multiple VLANs (comma-separated)",
                    ),
                ),
                (
                    "encapsulation_type",
                    models.CharField(
                        blank=True,
                        max_length=50,
                        help_text="Ethernet encapsulation and tagging method",
                    ),
                ),
                (
                    "interface_type",
                    models.CharField(
                        blank=True,
                        max_length=30,
                        help_text="Physical interface form factor",
                    ),
                ),
                (
                    "mtu_size",
                    models.PositiveIntegerField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(64),
                            django.core.validators.MaxValueValidator(16000),
                        ],
                        help_text="Maximum transmission unit size (bytes)",
                    ),
                ),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "verbose_name": "Ethernet Service Technical Data",
                "verbose_name_plural": "Ethernet Service Technical Data",
                "ordering": ("segment",),
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
        # ====================================================================
        # Migrate Data from JSON to Models
        # ====================================================================
        migrations.RunPython(migrate_json_to_models_forward, migrate_json_to_models_reverse),
    ]
