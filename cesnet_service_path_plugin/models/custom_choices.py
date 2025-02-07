from utilities.choices import ChoiceSet


class ExampleChoices(ChoiceSet):
    key = "KomoraServicePath.example_model_field"
    CHOICES = [
        ("active", "Active", "green"),
        ("deleted", "Deleted", "red"),
    ]
