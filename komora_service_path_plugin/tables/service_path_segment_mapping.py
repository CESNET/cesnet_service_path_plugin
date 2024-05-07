import django_tables2 as tables
from netbox.tables import NetBoxTable

from ..models import ServicePathSegmentMapping


class ServicePathSegmentMappingTable(NetBoxTable):
    segment = tables.Column(linkify=True)
    service_path = tables.Column(linkify=True)
    index = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = ServicePathSegmentMapping
        fields = ("pk", "id", "segment", "service_path", "index", "actions")
        default_columns = (
            "id",
            "segment",
            "service_path",
            "index",
        )
