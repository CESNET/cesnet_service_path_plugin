import django_tables2 as tables
from netbox.tables import NetBoxTable, columns

from komora_service_path_plugin.models import ServicePathSegmentMapping


class ServicePathSegmentMappingTable(NetBoxTable):
    id = tables.Column(verbose_name="ID", linkify=False)
    segment = tables.Column(linkify=True, verbose_name="Segment")
    service_path = tables.Column(linkify=True, verbose_name="Service Path")
    segment__site_a = tables.Column(linkify=True, verbose_name="Site A")
    segment__location_a = tables.Column(linkify=True, verbose_name="Location A")
    segment__site_b = tables.Column(linkify=True, verbose_name="Site B")
    segment__location_b = tables.Column(linkify=True, verbose_name="Location B")
    index = tables.Column()
    actions = columns.ActionsColumn(actions=(),)

    class Meta(NetBoxTable.Meta):
        model = ServicePathSegmentMapping
        fields = (
            "id",
            "segment",
            "segment__site_a",
            "segment__location_a",
            "segment__site_b",
            "segment__location_b",
            "service_path",
            "index",
            "actions",
        )
        default_columns = (
            "id",
            "segment",
            "segment__site_a",
            "segment__location_a",
            "segment__site_b",
            "segment__location_b",
            "service_path",
            "index",
        )
