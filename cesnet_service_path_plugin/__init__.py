"""Top-level package for Cesnet ServicePath Plugin."""

from netbox.plugins import PluginConfig
from .version import __version__, __author__, __description__, __name__


class CesnetServicePathPluginConfig(PluginConfig):
    name = __name__
    verbose_name = "Cesnet ServicePath Plugin"
    description = __description__
    version = __version__
    author = __author__
    base_url = "cesnet-service-path-plugin"

    def ready(self):
        # Call the original ready method
        super().ready()

        from netbox.models.features import register_models

        register_models(*self.get_models())


config = CesnetServicePathPluginConfig
