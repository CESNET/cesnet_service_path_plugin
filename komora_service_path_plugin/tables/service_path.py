import django_tables2 as tables
from netbox.tables import ChoiceFieldColumn, NetBoxTable, columns

from komora_service_path_plugin.models import ServicePath
from komora_service_path_plugin.models.sync_status_choices import DELETE_BUTTON


class ServicePathTable(NetBoxTable):
    tags = columns.TagColumn()
    name = tables.Column(linkify=True)
    sync_status = ChoiceFieldColumn()
    actions = columns.ActionsColumn(
        actions=("edit", "changelog"),
        extra_buttons=DELETE_BUTTON,
    )

    class Meta(NetBoxTable.Meta):
        model = ServicePath
        fields = (
            "pk",
            "name",
            "state",
            "kind",
            "komora_id",
            "tags",
            "actions",
            "sync_status",
        )
        default_columns = ("name", "state", "kind", "tags")
