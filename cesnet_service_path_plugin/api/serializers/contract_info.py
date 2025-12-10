# cesnet_service_path_plugin/api/serializers/contract_info.py
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from rest_framework.reverse import reverse

from cesnet_service_path_plugin.models import Segment, ContractInfo


class SegmentPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """
    Custom field that provides queryset dynamically to avoid circular imports
    """

    def get_queryset(self):
        return Segment.objects.all()


class ContractInfoSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:cesnet_service_path_plugin-api:contractinfo-detail"
    )

    # Writable segments field (M2M - accepts list of IDs for write operations)
    segments = SegmentPrimaryKeyRelatedField(many=True, required=False)

    # Versioning fields
    previous_version = serializers.PrimaryKeyRelatedField(
        queryset=ContractInfo.objects.all(),
        required=False,
        allow_null=True,
        help_text="Link to previous version for amendments/renewals"
    )
    contract_type = serializers.CharField(
        required=False,
        help_text="Type of contract (auto-set to 'amendment' if previous_version exists, can be set to 'renewal')"
    )
    # Read-only versioning fields
    superseded_by = serializers.PrimaryKeyRelatedField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    version = serializers.IntegerField(read_only=True)

    # Read-only computed fields
    total_recurring_cost = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_contract_value = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    commitment_end_date = serializers.DateField(read_only=True)

    class Meta:
        model = ContractInfo
        fields = [
            "id",
            "url",
            "display",
            # Versioning
            "previous_version",
            "superseded_by",
            "contract_type",
            "is_active",
            "version",
            # Contract metadata
            "contract_number",
            # Relationships
            "segments",
            # Financial
            "charge_currency",
            "recurring_charge",
            "recurring_charge_period",
            "number_of_recurring_charges",
            "non_recurring_charge",
            # Dates
            "start_date",
            "end_date",
            # Notes
            "notes",
            # Computed
            "total_recurring_cost",
            "total_contract_value",
            "commitment_end_date",
            # NetBox standard
            "created",
            "last_updated",
            "tags",
            "custom_fields",
        ]
        brief_fields = [
            "id",
            "url",
            "display",
            "contract_number",
            "contract_type",
            "is_active",
            "version",
            "recurring_charge",
            "charge_currency",
        ]

    def to_representation(self, instance):
        """
        Customize the output representation to show detailed segment info
        """
        ret = super().to_representation(instance)
        # Replace segments IDs with detailed info in the output
        if instance.segments.exists():
            ret["segments"] = self.get_segments_detail(instance)
        return ret

    def get_segments_detail(self, obj):
        """Return nested segment information for read operations"""
        segments_list = []
        request = self.context.get("request")

        for segment in obj.segments.all():
            if request:
                # API context - build absolute URI using reverse
                segment_url = reverse(
                    "plugins-api:cesnet_service_path_plugin-api:segment-detail",
                    kwargs={"pk": segment.id},
                    request=request,
                )
            else:
                # Non-API context (e.g., form validation) - use relative URL
                segment_url = reverse(
                    "plugins-api:cesnet_service_path_plugin-api:segment-detail", kwargs={"pk": segment.id}
                )

            segments_list.append({
                "id": segment.id,
                "url": segment_url,
                "display": str(segment),
                "name": segment.name,
            })

        return segments_list
