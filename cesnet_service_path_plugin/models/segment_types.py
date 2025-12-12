# cesnet_service_path_plugin/models/segment_types.py

from utilities.choices import ChoiceSet


class SegmentTypeChoices(ChoiceSet):
    """Choices for different types of network segments"""

    key = "cesnet_service_path_plugin.choices.segment_type"

    DARK_FIBER = "dark_fiber"
    OPTICAL_SPECTRUM = "optical_spectrum"
    ETHERNET_SERVICE = "ethernet_service"

    CHOICES = [
        (DARK_FIBER, "Dark Fiber", "purple"),
        (OPTICAL_SPECTRUM, "Optical Spectrum", "orange"),
        (ETHERNET_SERVICE, "Ethernet Service", "green"),
    ]
