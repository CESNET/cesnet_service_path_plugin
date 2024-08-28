from utilities.choices import ChoiceSet

DELETE_BUTTON = """
{% if record.sync_status == 'deleted' %}
<a class="btn btn-sm btn-danger" href="{{ record.get_absolute_url }}delete/?return_url={{request.path}}">
  <i class="mdi mdi-trash-can-outline" aria-hidden="true"></i>
</a>
{% endif %}
"""

class SyncStatusChoices(ChoiceSet):
    key = "KomoraServicePath.sync_status"
    CHOICES = [
        ("active", "Active", "green"),
        ("deleted", "Deleted", "red"),
    ]
