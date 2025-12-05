import django_tables2 as tables
from netbox.tables import ChoiceFieldColumn, NetBoxTable, columns

from cesnet_service_path_plugin.models import ContractInfo


class ContractInfoTable(NetBoxTable):
    """Table for displaying ContractInfo objects in list views."""

    tags = columns.TagColumn()

    # Main identifier with link to detail view
    contract_number = tables.Column(linkify=True)

    # Version chain relationships
    previous_version = tables.Column(linkify=True, verbose_name="Previous Version")
    superseded_by = tables.Column(linkify=True, verbose_name="Superseded By")

    # Choice fields with colored badges
    contract_type = ChoiceFieldColumn()
    charge_currency = ChoiceFieldColumn()
    recurring_charge_period = ChoiceFieldColumn()

    # Version and status columns using template columns
    version = tables.TemplateColumn(
        template_code="""
            <span class="badge text-bg-info">v{{ record.version }}</span>
        """,
        verbose_name="Version",
        orderable=False,
    )

    is_active = tables.TemplateColumn(
        template_code="""
            {% if record.is_active %}
                <span class="badge text-bg-success">Active</span>
            {% else %}
                <span class="badge text-bg-secondary">Superseded</span>
            {% endif %}
        """,
        verbose_name="Status",
        orderable=False,
    )

    # Financial columns with formatted display
    recurring_charge = tables.TemplateColumn(
        template_code="""
            {{ record.charge_currency }} {{ record.recurring_charge|floatformat:2 }}
        """,
        verbose_name="Recurring Charge",
        attrs={"td": {"class": "text-end"}},
    )

    non_recurring_charge = tables.TemplateColumn(
        template_code="""
            {% if record.non_recurring_charge %}
                {{ record.charge_currency }} {{ record.non_recurring_charge|floatformat:2 }}
            {% else %}
                <span class="text-muted">—</span>
            {% endif %}
        """,
        verbose_name="Non-Recurring Charge",
        attrs={"td": {"class": "text-end"}},
    )

    total_contract_value = tables.TemplateColumn(
        template_code="""
            <strong>{{ record.charge_currency }} {{ record.total_contract_value|floatformat:2 }}</strong>
        """,
        verbose_name="Total Value",
        attrs={"td": {"class": "text-end"}},
        orderable=False,
    )

    # Segments count with link
    segments = tables.TemplateColumn(
        template_code="""
            <span class="badge text-bg-secondary">{{ record.segments.count }}</span>
        """,
        verbose_name="Segments",
        orderable=False,
    )

    # Date fields
    start_date = tables.DateColumn(format="Y-m-d")
    end_date = tables.DateColumn(format="Y-m-d")

    # Text fields
    notes = tables.Column()

    # Computed field: number of recurring charges
    number_of_recurring_charges = tables.Column(
        verbose_name="# Charges",
        attrs={"td": {"class": "text-end"}},
    )

    class Meta(NetBoxTable.Meta):
        model = ContractInfo
        fields = (
            "pk",
            "id",
            "contract_number",
            "version",
            "is_active",
            "contract_type",
            "charge_currency",
            "recurring_charge",
            "recurring_charge_period",
            "number_of_recurring_charges",
            "non_recurring_charge",
            "total_contract_value",
            "start_date",
            "end_date",
            "segments",
            "previous_version",
            "superseded_by",
            "notes",
            "tags",
            "actions",
        )
        default_columns = (
            "contract_number",
            "version",
            "is_active",
            "contract_type",
            "recurring_charge",
            "total_contract_value",
            "start_date",
            "end_date",
            "segments",
        )
