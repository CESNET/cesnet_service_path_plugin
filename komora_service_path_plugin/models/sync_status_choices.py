from utilities.choices import ChoiceSet


class SyncStatusChoices(ChoiceSet):
    key = "KomoraServicePath.sync_status"
    CHOICES = [
        ("active", "Active", "green"),
        ("deleted", "Deleted", "red"),
    ]
