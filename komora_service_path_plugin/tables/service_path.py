import django_tables2 as tables
from netbox.tables import NetBoxTable, ChoiceFieldColumn

from . import service_path


class ServicePathTable(NetBoxTable):
    name = tables.Column(linkify=True)

    class Meta(NetBoxTable.Meta):
        model = None
        fields = ("pk", "id", "name", "actions")
        default_columns = ("name",)
