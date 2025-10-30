# cesnet_service_path_plugin/api/serializers/segment_financial_info.py
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from rest_framework.reverse import reverse

from cesnet_service_path_plugin.models import Segment, SegmentFinancialInfo


class SegmentPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """
    Custom field that provides queryset dynamically to avoid circular imports
    """

    def get_queryset(self):
        return Segment.objects.all()


class SegmentFinancialInfoSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:cesnet_service_path_plugin-api:segmentfinancialinfo-detail"
    )

    # Writable segment field (accepts ID for write operations)
    segment = SegmentPrimaryKeyRelatedField(required=True)

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
            "commitment_end_date",
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

    def to_representation(self, instance):
        """
        Customize the output representation to show detailed segment info
        """
        ret = super().to_representation(instance)
        # Replace segment ID with detailed info in the output
        if instance.segment:
            ret["segment"] = self.get_segment_detail(instance)
        return ret

    def get_segment_detail(self, obj):
        """Return nested segment information for read operations"""
        if obj.segment:
            # Check if we have a request in context
            request = self.context.get("request")

            if request:
                # API context - build absolute URI using reverse
                segment_url = reverse(
                    "plugins-api:cesnet_service_path_plugin-api:segment-detail",
                    kwargs={"pk": obj.segment.id},
                    request=request,
                )
            else:
                # Non-API context (e.g., form validation) - use relative URL
                segment_url = reverse(
                    "plugins-api:cesnet_service_path_plugin-api:segment-detail", kwargs={"pk": obj.segment.id}
                )

            return {
                "id": obj.segment.id,
                "url": segment_url,
                "display": str(obj.segment),
                "name": obj.segment.name,
            }
        return None
