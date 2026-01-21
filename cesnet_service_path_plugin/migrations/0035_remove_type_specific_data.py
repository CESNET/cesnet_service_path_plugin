# Generated migration for Phase 3 cleanup

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cesnet_service_path_plugin', '0034_add_type_specific_models'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='segment',
            name='type_specific_data',
        ),
    ]
