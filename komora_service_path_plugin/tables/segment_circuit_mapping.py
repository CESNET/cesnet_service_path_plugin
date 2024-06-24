import django_tables2 as tables
from netbox.tables import NetBoxTable, columns
from komora_service_path_plugin.models import SegmentCircuitMapping


class SegmentCircuitMappingTable(NetBoxTable):
    id = tables.Column(verbose_name="ID", linkify=False)
    segment = tables.Column(linkify=True, verbose_name="Segment", orderable=False)
    circuit = tables.Column(linkify=True, verbose_name="Circuit", orderable=False)
    actions = columns.ActionsColumn(actions=('delete', ),)

    class Meta(NetBoxTable.Meta):
        model = SegmentCircuitMapping
        fields = (
            "id",
            "segment",
            "circuit",
            "actions",
        )
        default_columns = (
            "segment",
            "circuit"
        )
