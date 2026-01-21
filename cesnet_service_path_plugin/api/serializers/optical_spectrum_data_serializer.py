from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer

from cesnet_service_path_plugin.models import OpticalSpectrumSegmentData, Segment


class OpticalSpectrumSegmentDataSerializer(NetBoxModelSerializer):
    """
    Serializer for OpticalSpectrumSegmentData model.

    Handles technical specifications for optical spectrum (DWDM/CWDM) segments
    including wavelength, spectral characteristics, dispersion, and modulation format.
    """

    # Read-only nested segment reference for GET operations
    segment = serializers.SerializerMethodField(read_only=True)

    # Write-only segment ID for POST/PUT/PATCH operations
    segment_id = serializers.PrimaryKeyRelatedField(
        queryset=Segment.objects.all(),
        source='segment',
        write_only=True,
        required=True,
        help_text="ID of the segment this technical data belongs to"
    )

    class Meta:
        model = OpticalSpectrumSegmentData
        fields = [
            'segment',
            'segment_id',
            'wavelength',
            'spectral_slot_width',
            'itu_grid_position',
            'chromatic_dispersion',
            'pmd_tolerance',
            'modulation_format',
            'created',
            'last_updated',
        ]

    def get_segment(self, obj):
        """Return basic segment info for GET operations"""
        request = self.context.get('request')
        if not request:
            return {
                'id': obj.segment.id,
                'name': obj.segment.name,
            }

        return {
            'id': obj.segment.id,
            'name': obj.segment.name,
            'url': request.build_absolute_uri(
                f'/api/plugins/cesnet-service-path-plugin/segments/{obj.segment.id}/'
            )
        }

    def validate(self, data):
        """
        Validate that the segment doesn't already have optical spectrum data.
        This is enforced by the OneToOne relationship, but we provide a clearer error message.
        Also triggers model-level validation (clean() method).
        """
        from django.core.exceptions import ValidationError as DjangoValidationError

        segment = data.get('segment')

        # Check if this is an update (instance exists) or create (new instance)
        if not self.instance and segment:
            # Creating new instance - check if segment already has data
            if hasattr(segment, 'optical_spectrum_data'):
                raise serializers.ValidationError({
                    'segment': f'Segment "{segment.name}" already has optical spectrum technical data.'
                })

        # Trigger model-level validation by creating a temporary instance
        # This ensures model's clean() method is called
        if self.instance:
            # Updating existing instance
            instance = self.instance
            for key, value in data.items():
                setattr(instance, key, value)
        else:
            # Creating new instance
            instance = OpticalSpectrumSegmentData(**data)

        try:
            instance.clean()
        except DjangoValidationError as e:
            # Convert Django ValidationError to DRF ValidationError
            raise serializers.ValidationError(e.message_dict if hasattr(e, 'message_dict') else str(e))

        return data
