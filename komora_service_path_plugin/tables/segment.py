import django_tables2 as tables
from netbox.tables import NetBoxTable, ChoiceFieldColumn

from ..models import Segment


class SegmentTable(NetBoxTable):
    name = tables.Column(linkify=True)

    class Meta(NetBoxTable.Meta):
        model = Segment
        fields = ("pk", "id", "name", "actions", "komora_id")
        default_columns = ("name",)
