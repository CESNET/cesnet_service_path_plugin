"""Top-level package for Cesnet ServicePath Plugin."""

from importlib import metadata
from netbox.plugins import PluginConfig

# Get package metadata from pyproject.toml
_metadata = metadata.metadata("cesnet_service_path_plugin")
__version__ = _metadata["Version"]
__description__ = _metadata["Summary"]
__name__ = _metadata["Name"]
__author__ = _metadata["Author"]
__email__ = _metadata["Author-email"]


class CesnetServicePathPluginConfig(PluginConfig):
    name = __name__
    verbose_name = "Cesnet ServicePath Plugin"
    description = __description__
    version = __version__
    base_url = "cesnet-service-path-plugin"
    author = __email__


config = CesnetServicePathPluginConfig
