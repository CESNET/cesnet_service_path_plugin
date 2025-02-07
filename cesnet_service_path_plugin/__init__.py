"""Top-level package for Cesnet ServicePath Plugin."""

from netbox.plugins import PluginConfig
from .version import __version__, __author__, __email__, __description__, __name__


class CesnetServicePathPluginConfig(PluginConfig):
    name = __name__
    verbose_name = "Cesnet ServicePath Plugin"
    description = __description__
    version = __version__
    base_url = "cesnet-service-path-plugin"


config = CesnetServicePathPluginConfig
