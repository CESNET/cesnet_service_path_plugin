import django_tables2 as tables
from netbox.tables import NetBoxTable

from cesnet_service_path_plugin.models import SegmentCircuitMapping


class SegmentCircuitMappingTable(NetBoxTable):
    segment = tables.Column(linkify=True, verbose_name="Segment", orderable=True, order_by=("segment__name",))
    segment_network_label = tables.Column(
        linkify=False,
        verbose_name="Network Label",
        orderable=True,
        order_by=("segment__network_label",),
        accessor="segment.network_label",
    )
    segment_site_a = tables.Column(
        linkify=True,
        verbose_name="Site A",
        orderable=True,
        order_by=("segment__site_a__name",),
        accessor="segment.site_a",
    )
    segment_location_a = tables.Column(
        linkify=True,
        verbose_name="Location A",
        orderable=True,
        order_by=("segment__location_a__name",),
        accessor="segment.location_a",
    )
    segment_site_b = tables.Column(
        linkify=True,
        verbose_name="Site B",
        orderable=True,
        order_by=("segment__site_b__name",),
        accessor="segment.site_b",
    )
    segment_location_b = tables.Column(
        linkify=True,
        verbose_name="Location B",
        orderable=True,
        order_by=("segment__location_b__name",),
        accessor="segment.location_b",
    )
    circuit = tables.Column(linkify=True, verbose_name="Circuit", orderable=True, order_by=("circuit__name",))

    class Meta(NetBoxTable.Meta):
        model = SegmentCircuitMapping
        fields = (
            "id",
            "circuit",
            "segment",
            "segment_network_label",
            "segment_site_a",
            "segment_location_a",
            "segment_site_b",
            "segment_location_b",
            "actions",
        )
        default_columns = (
            "circuit",
            "segment",
            "segment_network_label",
            "segment_site_a",
            "segment_site_b",
        )
