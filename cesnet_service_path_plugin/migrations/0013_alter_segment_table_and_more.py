from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        (
            "cesnet_service_path_plugin",
            "0012_segment_sync_status_servicepath_sync_status",
        ),
    ]

    operations = [
        migrations.RunSQL(
            """
            ALTER TABLE IF EXISTS komora_service_path_plugin_segment 
            RENAME TO cesnet_service_path_plugin_segment;

            ALTER TABLE IF EXISTS komora_service_path_plugin_segmentcircuitmapping 
            RENAME TO cesnet_service_path_plugin_segmentcircuitmapping;

            ALTER TABLE IF EXISTS komora_service_path_plugin_servicepath 
            RENAME TO cesnet_service_path_plugin_servicepath;

            ALTER TABLE IF EXISTS komora_service_path_plugin_servicepathsegmentmapping 
            RENAME TO cesnet_service_path_plugin_servicepathsegmentmapping;
        """,
            """
            ALTER TABLE IF EXISTS cesnet_service_path_plugin_segment 
            RENAME TO komora_service_path_plugin_segment;

            ALTER TABLE IF EXISTS cesnet_service_path_plugin_segmentcircuitmapping 
            RENAME TO komora_service_path_plugin_segmentcircuitmapping;

            ALTER TABLE IF EXISTS cesnet_service_path_plugin_servicepath 
            RENAME TO komora_service_path_plugin_servicepath;

            ALTER TABLE IF EXISTS cesnet_service_path_plugin_servicepathsegmentmapping 
            RENAME TO komora_service_path_plugin_servicepathsegmentmapping;
        """,
        )
    ]
