from utilities.choices import ChoiceSet


class StatusChoices(ChoiceSet):
    key = "cesnet_service_path_plugin.choices.status"

    ACTIVE = "active"
    PLANNED = "planned"
    OFFLINE = "offline"

    CHOICES = [
        (ACTIVE, "Active", "green"),
        (PLANNED, "Planned", "orange"),
        (OFFLINE, "Offline", "red"),
    ]


class KindChoices(ChoiceSet):
    key = "cesnet_service_path_plugin.choices.kind"

    EXPERIMENTAL = "experimental"
    CORE = "core"
    CUSTOMER = "customer"

    CHOICES = [
        (EXPERIMENTAL, "Experimentální", "cyan"),
        (CORE, "Páteřní", "blue"),
        (CUSTOMER, "Zákaznická", "green"),
    ]
