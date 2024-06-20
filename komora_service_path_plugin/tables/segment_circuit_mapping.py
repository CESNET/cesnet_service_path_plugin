import django_tables2 as tables
from netbox.tables import NetBoxTable

from komora_service_path_plugin.models import SegmentCircuitMapping


class SegmentCircuitMappingTable(NetBoxTable):
    segment = tables.Column(linkify=True, verbose_name="Segment")
    circuit = tables.Column(linkify=True, verbose_name="Service Path")
    # segment__site_a = tables.Column(linkify=True, verbose_name="Site A")
    # segment__location_a = tables.Column(linkify=True, verbose_name="Location A")
    # segment__site_b = tables.Column(linkify=True, verbose_name="Site B")
    # segment__location_b = tables.Column(linkify=True, verbose_name="Location B")
    # index = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = SegmentCircuitMapping
        fields = (
            "pk",
            "id",
            "segment",
            # "segment__site_a",
            # "segment__location_a",
            # "segment__site_b",
            # "segment__location_b",
            # "index",
            "circuit",
            "actions",
        )
        default_columns = (
            "id",
            "segment",
            # "segment__site_a",
            # "segment__location_a",
            # "segment__site_b",
            # "segment__location_b",
            # "index",
            "circuit"
        )
