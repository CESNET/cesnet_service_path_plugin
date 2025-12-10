from utilities.choices import ChoiceSet


class StatusChoices(ChoiceSet):
    key = "cesnet_service_path_plugin.choices.status"

    ACTIVE = "active"
    PLANNED = "planned"
    OFFLINE = "offline"
    DECOMMISSIONED = "decommissioned"
    SURVEYED = "surveyed"

    CHOICES = [
        (ACTIVE, "Active", "green"),
        (PLANNED, "Planned", "orange"),
        (OFFLINE, "Offline", "red"),
        (DECOMMISSIONED, "Decommissioned", "gray"),
        (SURVEYED, "Surveyed", "blue"),
    ]


class OwnershipTypeChoices(ChoiceSet):
    """
    owned
    leased
    shared
    foreign
    """

    key = "cesnet_service_path_plugin.choices.ownership_type"
    OWNED = "owned"
    LEASED = "leased"
    SHARED = "shared"
    FOREIGN = "foreign"

    CHOICES = [
        (OWNED, "Owned", "green"),
        (LEASED, "Leased", "blue"),
        (SHARED, "Shared", "yellow"),
        (FOREIGN, "Foreign", "red"),
    ]


class KindChoices(ChoiceSet):
    key = "cesnet_service_path_plugin.choices.kind"

    EXPERIMENTAL = "experimental"
    CORE = "core"
    CUSTOMER = "customer"

    CHOICES = [
        (EXPERIMENTAL, "Experimental", "cyan"),
        (CORE, "Core", "blue"),
        (CUSTOMER, "Customer", "green"),
    ]


class ContractTypeChoices(ChoiceSet):
    """
    Contract type indicates how the contract was created.
    - New: Original contract
    - Renewal: New contract period after previous expired
    - Amendment: Modification to existing contract terms
    """

    key = "cesnet_service_path_plugin.choices.contract_type"

    NEW = "new"
    RENEWAL = "renewal"
    AMENDMENT = "amendment"

    CHOICES = [
        (NEW, "New Contract", "blue"),
        (RENEWAL, "Renewal", "green"),
        (AMENDMENT, "Amendment", "orange"),
    ]


class CurrencyChoices(ChoiceSet):
    """
    Currency codes following ISO 4217 standard.
    Default choices can be overridden in plugin configuration.
    """

    key = "cesnet_service_path_plugin.choices.currency"

    CZK = "CZK"
    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"
    PLN = "PLN"
    HUF = "HUF"

    CHOICES = [
        (CZK, "Czech Koruna (CZK)", "blue"),
        (EUR, "Euro (EUR)", "green"),
        (USD, "US Dollar (USD)", "cyan"),
        (GBP, "British Pound (GBP)", "purple"),
        (PLN, "Polish Zloty (PLN)", "orange"),
        (HUF, "Hungarian Forint (HUF)", "yellow"),
    ]


class RecurringChargePeriodChoices(ChoiceSet):
    """
    Frequency of recurring charges in contracts.
    """

    key = "cesnet_service_path_plugin.choices.recurring_charge_period"

    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUALLY = "semi_annually"
    ANNUALLY = "annually"

    CHOICES = [
        (MONTHLY, "Monthly", "blue"),
        (QUARTERLY, "Quarterly", "green"),
        (SEMI_ANNUALLY, "Semi-Annually", "orange"),
        (ANNUALLY, "Annually", "purple"),
    ]
