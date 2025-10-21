# cesnet_service_path_plugin/api/serializers/segment_financial_info.py
from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer

from cesnet_service_path_plugin.models import SegmentFinancialInfo


class SegmentFinancialInfoSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:cesnet_service_path_plugin-api:segmentfinancialinfo-detail"
    )

    # Nested representation of the segment
    segment = serializers.SerializerMethodField(read_only=True)

    # Read-only computed fields
    total_commitment_cost = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_cost_including_setup = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = SegmentFinancialInfo
        fields = [
            "id",
            "url",
            "display",
            "segment",
            "monthly_charge",
            "charge_currency",
            "non_recurring_charge",
            "commitment_period_months",
            "notes",
            "total_commitment_cost",
            "total_cost_including_setup",
            "created",
            "last_updated",
            "tags",
            "custom_fields",
        ]
        brief_fields = [
            "id",
            "url",
            "display",
            "segment",
            "monthly_charge",
            "charge_currency",
        ]

    def get_segment(self, obj):
        """Return nested segment information"""
        if obj.segment:
            return {
                "id": obj.segment.id,
                "url": self.context["request"].build_absolute_uri(
                    f"/api/plugins/cesnet-service-path-plugin/segments/{obj.segment.id}/"
                ),
                "display": str(obj.segment),
                "name": obj.segment.name,
            }
        return None
