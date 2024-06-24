import django_tables2 as tables
from netbox.tables import NetBoxTable, columns
from komora_service_path_plugin.models import ServicePathCircuitMapping


class ServicePathCircuitMappingTable(NetBoxTable):
    id = tables.Column(verbose_name="ID", linkify=False)
    service_path = tables.Column(linkify=True, verbose_name="Service Path", orderable=False)
    circuit = tables.Column(linkify=True, verbose_name="Circuit", orderable=False)
    actions = columns.ActionsColumn(actions=('delete', ),)

    class Meta(NetBoxTable.Meta):
        model = ServicePathCircuitMapping
        fields = (
            "id",
            "service_path",
            "circuit",
            "actions",
        )
        default_columns = (
            "service_path",
            "circuit"
        )
