import django_tables2 as tables
from netbox.tables import NetBoxTable, ChoiceFieldColumn

from ..models import SegmentPath


class SegmentPathTable(NetBoxTable):
    name = tables.Column(linkify=True)

    class Meta(NetBoxTable.Meta):
        model = SegmentPath
        fields = ("pk", "id", "name", "actions")
        default_columns = ("name",)
