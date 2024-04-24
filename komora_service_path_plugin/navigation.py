from django.conf import settings

from extras.plugins import PluginMenuButton, PluginMenuItem, PluginMenu
from utilities.choices import ButtonColorChoices

segment_plugin_buttons = [
    PluginMenuButton(
        link="plugins:komora_service_path_plugin:servicepath_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
        color=ButtonColorChoices.GREEN,
    ),
]

service_plugin_buttons = [
    PluginMenuButton(
        link="plugins:komora_service_path_plugin:segment_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
        color=ButtonColorChoices.GREEN,
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
)

menu = PluginMenu(
    label="Komora Service Paths",
    groups=(("", _menu_items),),
    icon_class="mdi mdi-map",
)
