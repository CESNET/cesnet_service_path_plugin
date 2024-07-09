import django_tables2 as tables
from netbox.tables import NetBoxTable, columns
from komora_service_path_plugin.models import Segment


class SegmentTable(NetBoxTable):
    name = tables.Column(linkify=True)
    actions = columns.ActionsColumn(actions=("changelog",),)

    class Meta(NetBoxTable.Meta):
        model = Segment
        fields = ("pk", "id", "name", "actions", "komora_id")
        default_columns = ("name",)
