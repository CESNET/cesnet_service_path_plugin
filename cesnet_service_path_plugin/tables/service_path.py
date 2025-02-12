import django_tables2 as tables
from netbox.tables import ChoiceFieldColumn, NetBoxTable, columns

from cesnet_service_path_plugin.models import ServicePath


class ServicePathTable(NetBoxTable):
    tags = columns.TagColumn()
    name = tables.Column(linkify=True)
    status = ChoiceFieldColumn()
    kind = ChoiceFieldColumn()

    class Meta(NetBoxTable.Meta):
        model = ServicePath
        fields = (
            "pk",
            "name",
            "status",
            "kind",
            "tags",
            "actions",
        )
        default_columns = ("name", "status", "kind", "tags")
