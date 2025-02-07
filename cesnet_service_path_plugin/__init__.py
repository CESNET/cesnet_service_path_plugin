"""Top-level package for Komora ServicePath Plugin."""

from netbox.plugins import PluginConfig
from .version import __version__, __author__, __email__, __description__, __name__


class KomoraServicePathPluginConfig(PluginConfig):
    name = __name__
    verbose_name = "Komora ServicePath Plugin"
    description = __description__
    version = __version__
    base_url = "komora-service-path-plugin"


config = KomoraServicePathPluginConfig
