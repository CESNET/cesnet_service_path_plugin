import django_tables2 as tables
from netbox.tables import ChoiceFieldColumn, NetBoxTable, columns

from cesnet_service_path_plugin.models import Segment


class SegmentTable(NetBoxTable):
    tags = columns.TagColumn()
    name = tables.Column(linkify=True)
    status = ChoiceFieldColumn()
    segment_type = ChoiceFieldColumn()
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

    # New column for path data status
    has_path_data = tables.TemplateColumn(
        template_code="""
            {% include 'cesnet_service_path_plugin/inc/path_data_badge.html' %}
        """,
        verbose_name="Path Data",
        orderable=False,
        attrs={"td": {"class": "text-center"}},  # Center the column content
    )

    # Optional: Path length column (only shows when there's data)
    path_length = tables.TemplateColumn(
        template_code="""
            {% include 'cesnet_service_path_plugin/inc/path_length.html' %}
        """,
        verbose_name="Path Length",
        orderable=True,
        attrs={"td": {"class": "text-end"}},  # Right-align numbers
    )

    class Meta(NetBoxTable.Meta):
        model = Segment
        fields = (
            "pk",
            "id",
            "name",
            "segment_type",
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
            "has_path_data",  # New field
            "path_length",  # New field
            "tags",
            "actions",
            "status",
            "date_status",
        )

        default_columns = (
            "name",
            "segment_type",
            "network_label",
            "provider",
            "site_a",
            "location_a",
            "site_b",
            "location_b",
            "has_path_data",  # Added to default view
            "status",
            "date_status",
        )
