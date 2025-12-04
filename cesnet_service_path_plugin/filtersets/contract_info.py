import django_filters
from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet

from cesnet_service_path_plugin.models import ContractInfo
from cesnet_service_path_plugin.models.custom_choices import (
    ContractTypeChoices,
    CurrencyChoices,
    RecurringChargePeriodChoices,
)


class ContractInfoFilterSet(NetBoxModelFilterSet):
    """FilterSet for ContractInfo model with versioning support"""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    contract_number = django_filters.CharFilter(lookup_expr="icontains")
    contract_type = django_filters.MultipleChoiceFilter(choices=ContractTypeChoices)
    charge_currency = django_filters.MultipleChoiceFilter(choices=CurrencyChoices)
    recurring_charge_period = django_filters.MultipleChoiceFilter(choices=RecurringChargePeriodChoices)

    # Date filters
    start_date = django_filters.DateFilter()
    end_date = django_filters.DateFilter()

    # Version chain filters
    is_active = django_filters.BooleanFilter(
        method="_filter_is_active",
        label="Is Active (Not Superseded)",
    )

    has_previous_version = django_filters.BooleanFilter(
        method="_filter_has_previous_version",
        label="Has Previous Version",
    )

    class Meta:
        model = ContractInfo
        fields = [
            "id",
            "contract_number",
            "contract_type",
            "charge_currency",
            "recurring_charge_period",
            "start_date",
            "end_date",
        ]

    def _filter_is_active(self, queryset, name, value):
        """
        Filter contracts by is_active status.
        A contract is active if superseded_by is NULL.
        """
        if value is None:
            return queryset

        if value:
            # Show only active contracts (not superseded)
            return queryset.filter(superseded_by__isnull=True)
        else:
            # Show only superseded contracts
            return queryset.filter(superseded_by__isnull=False)

    def _filter_has_previous_version(self, queryset, name, value):
        """
        Filter contracts by whether they have a previous version.
        """
        if value is None:
            return queryset

        if value:
            # Show only contracts with previous versions
            return queryset.filter(previous_version__isnull=False)
        else:
            # Show only contracts without previous versions (v1)
            return queryset.filter(previous_version__isnull=True)

    def search(self, queryset, name, value):
        """Full-text search across contract fields"""
        contract_number = Q(contract_number__icontains=value)
        notes = Q(notes__icontains=value)

        return queryset.filter(
            contract_number | notes
        )
