import django_tables2 as tables
from netbox.tables import NetBoxTable, columns

from ..models import ServicePath


class ServicePathTable(NetBoxTable):
    name = tables.Column(linkify=True)
    actions = columns.ActionsColumn(actions=("changelog",),)

    class Meta(NetBoxTable.Meta):
        model = ServicePath
        fields = ("pk", "name", "state", "kind", "komora_id", "actions")
        default_columns = ("name", "state", "kind")
