from netbox.plugins import PluginMenuButton, PluginMenuItem, PluginMenu

service_plugin_buttons = [
    PluginMenuButton(
        link="plugins:komora_service_path_plugin:servicepath_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
    ),
]


_menu_items = (
    PluginMenuItem(
        link="plugins:komora_service_path_plugin:segment_list",
        link_text="Segments",
    ),
    PluginMenuItem(
        link="plugins:komora_service_path_plugin:servicepath_list",
        link_text="Service Paths",
        buttons=service_plugin_buttons,
    ),
    PluginMenuItem(
        link="plugins:komora_service_path_plugin:servicepathsegmentmapping_list",
        link_text="Segment Mappings",
    ),

)

_circuits_menu_items = (
    PluginMenuItem(
        link="plugins:komora_service_path_plugin:servicepathcircuitmapping_list",
        link_text="Service Path - Circuit",
    ),
    PluginMenuItem(
        link="plugins:komora_service_path_plugin:segmentcircuitmapping_list",
        link_text="Segment - Circuit",
    ),
)

menu = PluginMenu(
    label="Komora Service Paths",
    groups=(("Komora", _menu_items),
            ("Circuits Mappings", _circuits_menu_items)),
    icon_class="mdi mdi-map",
)
