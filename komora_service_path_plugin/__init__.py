"""Top-level package for Komora ServicePath Plugin."""

__author__ = """Jan Krupa"""
__email__ = "jan.krupa@cesnet.cz"
__version__ = "0.1.0"  # change according to setup.py or pyprojet.toml


from extras.plugins import PluginConfig


class KomoraServicePathPluginConfig(PluginConfig):
    name = "komora_service_path_plugin"
    verbose_name = "Komora ServicePath Plugin"
    description = "Synchronize data between Komora and NetBox. Copies Segment and Service Paths from Komora."
    version = __version__
    base_url = "komora_service_path_plugin"


config = KomoraServicePathPluginConfig
