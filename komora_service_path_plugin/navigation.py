from netbox.plugins import PluginMenuItem, PluginMenu

_menu_items = (
    PluginMenuItem(
        link="plugins:komora_service_path_plugin:segment_list",
        link_text="Segments",
    ),
    PluginMenuItem(
        link="plugins:komora_service_path_plugin:servicepath_list",
        link_text="Service Paths",
    ),
)

_mappings_menu_items = (
    PluginMenuItem(
        link="plugins:komora_service_path_plugin:servicepathsegmentmapping_list",
        link_text="Segment - Service Path",
    ),
    PluginMenuItem(
        link="plugins:komora_service_path_plugin:segmentcircuitmapping_list",
        link_text="Segment - Circuit",
    ),
)

menu = PluginMenu(
    label="Komora Service Paths",
    groups=(("Komora", _menu_items),
            ("Mappings", _mappings_menu_items)),
    icon_class="mdi mdi-map",
)
