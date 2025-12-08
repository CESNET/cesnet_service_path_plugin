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

    end_date = tables.TemplateColumn(
        template_code="""
            {% if record.end_date %}
                <span class="badge text-bg-{{ record.get_end_date_color }}"
                      title="{{ record.get_end_date_tooltip }}">
                    {{ record.end_date }}
                </span>
            {% else %}
                <span class="text-muted">—</span>
            {% endif %}
        """,
        verbose_name="End Date",
    )

    commitment_end_date = tables.TemplateColumn(
        template_code="""
            {% if record.commitment_end_date %}
                <span class="badge text-bg-{{ record.get_commitment_end_date_color }}"
                      title="{{ record.get_commitment_end_date_tooltip }}">
                    {{ record.commitment_end_date }}
                </span>
            {% else %}
                <span class="text-muted">—</span>
            {% endif %}
        """,
        verbose_name="Commitment End Date",
        orderable=False,
    )

    # Text fields
    notes = tables.Column()

    # Computed field: number of recurring charges
    number_of_recurring_charges = tables.Column(
        verbose_name="# Charges",
        attrs={"td": {"class": "text-end"}},
    )

    # Actions column with custom "New Version" button for active contracts
    actions = columns.ActionsColumn(
        extra_buttons="""
        {% load helpers %}
        {% if record.is_active and perms.cesnet_service_path_plugin.add_contractinfo %}
            {% action_url record 'add' as clone_url %}
            <a href="{{ clone_url }}?previous_version={{ record.pk }}&contract_number={{ record.contract_number|urlencode }}&charge_currency={{ record.charge_currency }}&recurring_charge={{ record.recurring_charge }}&recurring_charge_period={{ record.recurring_charge_period }}&number_of_recurring_charges={{ record.number_of_recurring_charges }}&non_recurring_charge={{ record.non_recurring_charge }}{% if record.start_date %}&start_date={{ record.start_date|date:'Y-m-d' }}{% endif %}{% if record.end_date %}&end_date={{ record.end_date|date:'Y-m-d' }}{% endif %}{% if record.notes %}&notes={{ record.notes|urlencode }}{% endif %}{% for segment in record.segments.all %}&segments={{ segment.pk }}{% endfor %}"
               title="Create New Version"
               class="btn btn-sm btn-success">
                <i class="mdi mdi-content-copy" aria-hidden="true"></i>
            </a>
        {% endif %}
        """
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
            "commitment_end_date",
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
            "commitment_end_date",
            "segments",
        )
