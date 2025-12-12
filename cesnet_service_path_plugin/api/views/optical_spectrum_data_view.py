from netbox.api.viewsets import NetBoxModelViewSet

from cesnet_service_path_plugin.models import OpticalSpectrumSegmentData
from cesnet_service_path_plugin.api.serializers.optical_spectrum_data_serializer import (
    OpticalSpectrumSegmentDataSerializer,
)


class OpticalSpectrumSegmentDataViewSet(NetBoxModelViewSet):
    """
    API viewset for managing Optical Spectrum (DWDM/CWDM) technical data.

    Provides CRUD operations for optical spectrum segment technical specifications.
    """

    queryset = OpticalSpectrumSegmentData.objects.select_related('segment').all()
    serializer_class = OpticalSpectrumSegmentDataSerializer
