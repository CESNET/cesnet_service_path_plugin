from django.db import migrations


def copy_state_to_status(apps, schema_editor):
    ServicePath = apps.get_model("cesnet_service_path_plugin", "ServicePath")

    # Define mapping from state to status
    state_to_status = {
        "active": "active",
        "planned": "planned",
        "decommissioned": "decommissioned",
    }

    for service_path in ServicePath.objects.all():
        # Get the corresponding status value or default to 'active' if not found
        new_status = state_to_status.get(service_path.state.lower(), "active")
        service_path.status = new_status
        service_path.save()


def reverse_copy_state_to_status(apps, schema_editor):
    ServicePath = apps.get_model("cesnet_service_path_plugin", "ServicePath")

    # Define reverse mapping from status to state
    status_to_state = {
        "active": "active",
        "planned": "planned",
        "decommissioned": "decommissioned",
    }

    for service_path in ServicePath.objects.all():
        # Get the corresponding state value or default to 'active' if not found
        old_state = status_to_state.get(service_path.status.lower(), "active")
        service_path.state = old_state
        service_path.save()


class Migration(migrations.Migration):
    dependencies = [
        (
            "cesnet_service_path_plugin",
            "0020_add_field_status_to_segment_and_servicepath",
        ),
    ]

    operations = [
        migrations.RunPython(copy_state_to_status, reverse_copy_state_to_status)
    ]
