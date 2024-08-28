import django_tables2 as tables
from netbox.tables import ChoiceFieldColumn, NetBoxTable, columns

from komora_service_path_plugin.models import Segment
from komora_service_path_plugin.models.sync_status_choices import DELETE_BUTTON


class SegmentTable(NetBoxTable):
    tags = columns.TagColumn()
    name = tables.Column(linkify=True)
    sync_status = ChoiceFieldColumn()
    provider = tables.Column(linkify=True)
    site_a = tables.Column(linkify=True)
    location_a = tables.Column(linkify=True)
    device_a = tables.Column(linkify=True)
    port_a = tables.Column(linkify=True)
    site_b = tables.Column(linkify=True)
    location_b = tables.Column(linkify=True)
    device_b = tables.Column(linkify=True)
    port_b = tables.Column(linkify=True)
    actions = columns.ActionsColumn(
        actions=("edit", "changelog"),
        extra_buttons=DELETE_BUTTON,
    )

    class Meta(NetBoxTable.Meta):
        model = Segment
        fields = (
            "pk",
            "id",
            "name",
            "komora_id",
            "network_label",
            "install_date",
            "termination_date",
            "provider",
            "provider_segment_id",
            "provider_segment_name",
            "provider_segment_contract",
            "site_a",
            "location_a",
            "device_a",
            "port_a",
            "site_b",
            "location_b",
            "device_b",
            "port_b",
            "tags",
            "actions",
            "sync_status",
        )

        default_columns = (
            "name",
            "network_label",
            "provider",
            "site_a",
            "location_a",
            "site_b",
            "location_b",
        )
