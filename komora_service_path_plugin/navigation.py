from django.conf import settings

from netbox.plugins import PluginMenuButton, PluginMenuItem, PluginMenu

segment_plugin_buttons = [
    PluginMenuButton(
        link="plugins:komora_service_path_plugin:servicepath_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
    ),
]

service_plugin_buttons = [
    PluginMenuButton(
        link="plugins:komora_service_path_plugin:segment_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
    ),
]


_menu_items = (
    PluginMenuItem(
        link="plugins:komora_service_path_plugin:segment_list",
        link_text="Segments",
        buttons=segment_plugin_buttons,
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

menu = PluginMenu(
    label="Komora Service Paths",
    groups=(("", _menu_items),),
    icon_class="mdi mdi-map",
)
