from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

_menu_items = (
    PluginMenuItem(
        link="plugins:cesnet_service_path_plugin:segment_list",
        link_text="Segments",
        buttons=(
            PluginMenuButton(
                link="plugins:cesnet_service_path_plugin:segment_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
            ),
            PluginMenuButton(
                link="plugins:cesnet_service_path_plugin:segment_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:cesnet_service_path_plugin:segments_map",
        link_text="Segments Map",
    ),
    PluginMenuItem(
        link="plugins:cesnet_service_path_plugin:servicepath_list",
        link_text="Service Paths",
        buttons=(
            PluginMenuButton(
                link="plugins:cesnet_service_path_plugin:servicepath_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
            ),
            PluginMenuButton(
                link="plugins:cesnet_service_path_plugin:servicepath_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
            ),
        ),
    ),
)

_mappings_menu_items = (
    PluginMenuItem(
        link="plugins:cesnet_service_path_plugin:servicepathsegmentmapping_list",
        link_text="Segment - Service Path",
        buttons=(
            PluginMenuButton(
                link="plugins:cesnet_service_path_plugin:servicepathsegmentmapping_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
            ),
            PluginMenuButton(
                link="plugins:cesnet_service_path_plugin:servicepathsegmentmapping_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:cesnet_service_path_plugin:segmentcircuitmapping_list",
        link_text="Segment - Circuit",
        buttons=(
            PluginMenuButton(
                link="plugins:cesnet_service_path_plugin:segmentcircuitmapping_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
            ),
            PluginMenuButton(
                link="plugins:cesnet_service_path_plugin:segmentcircuitmapping_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
            ),
        ),
    ),
)

menu = PluginMenu(
    label="Service Paths",
    groups=(("Main", _menu_items), ("Mappings", _mappings_menu_items)),
    icon_class="mdi mdi-map",
)
