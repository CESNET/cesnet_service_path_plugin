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
