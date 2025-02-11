import django_tables2 as tables
from netbox.tables import ChoiceFieldColumn, NetBoxTable, columns

from cesnet_service_path_plugin.models import Segment


class SegmentTable(NetBoxTable):
    tags = columns.TagColumn()
    name = tables.Column(linkify=True)
    status = ChoiceFieldColumn()
    provider = tables.Column(linkify=True)
    site_a = tables.Column(linkify=True)
    location_a = tables.Column(linkify=True)
    site_b = tables.Column(linkify=True)
    location_b = tables.Column(linkify=True)

    date_status = tables.TemplateColumn(
        template_code="""
            {% include 'cesnet_service_path_plugin/inc/date_status_badge.html' %}
        """,
        verbose_name="Date Status",
        orderable=False,
    )

    class Meta(NetBoxTable.Meta):
        model = Segment
        fields = (
            "pk",
            "id",
            "name",
            "network_label",
            "install_date",
            "termination_date",
            "provider",
            "provider_segment_id",
            "provider_segment_name",
            "provider_segment_contract",
            "site_a",
            "location_a",
            "site_b",
            "location_b",
            "tags",
            "actions",
            "status",
            "date_status",
        )

        default_columns = (
            "name",
            "network_label",
            "provider",
            "site_a",
            "location_a",
            "site_b",
            "location_b",
            "status",
            "date_status",
        )
