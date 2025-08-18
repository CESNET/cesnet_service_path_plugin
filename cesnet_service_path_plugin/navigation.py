from netbox.plugins import PluginMenuItem, PluginMenu

_menu_items = (
    PluginMenuItem(
        link="plugins:cesnet_service_path_plugin:segment_list",
        link_text="Segments",
    ),
    PluginMenuItem(
        link="plugins:cesnet_service_path_plugin:segments_map",
        link_text="Segments Map",
    ),
    PluginMenuItem(
        link="plugins:cesnet_service_path_plugin:servicepath_list",
        link_text="Service Paths",
    ),
)

_mappings_menu_items = (
    PluginMenuItem(
        link="plugins:cesnet_service_path_plugin:servicepathsegmentmapping_list",
        link_text="Segment - Service Path",
    ),
    PluginMenuItem(
        link="plugins:cesnet_service_path_plugin:segmentcircuitmapping_list",
        link_text="Segment - Circuit",
    ),
)

menu = PluginMenu(
    label="Service Paths",
    groups=(("Main", _menu_items), ("Mappings", _mappings_menu_items)),
    icon_class="mdi mdi-map",
)
