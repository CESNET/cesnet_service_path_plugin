from decimal import Decimal
from django.db import models
from django.urls import reverse
from django.utils import timezone
from netbox.models import NetBoxModel
from dateutil.relativedelta import relativedelta

from cesnet_service_path_plugin.models.custom_choices import (
    ContractTypeChoices,
    CurrencyChoices,
    RecurringChargePeriodChoices,
)


class ContractInfo(NetBoxModel):
    """
    ContractInfo model representing legal agreements for network segments.
    Supports version history through a linear chain using previous_version/superseded_by.
    """

    # ========================================================================
    # VERSION CHAIN - Linear linked list for contract history
    # ========================================================================
    previous_version = models.OneToOneField(
        "self",
        on_delete=models.PROTECT,  # Can't delete if newer versions exist
        null=True,
        blank=True,
        related_name="next_version_relation",
        editable=False,
        help_text="Previous version of this contract (creates linear chain)",
    )

    superseded_by = models.OneToOneField(
        "self",
        on_delete=models.SET_NULL,  # If newer version deleted, this becomes active
        null=True,
        blank=True,
        related_name="supersedes",
        editable=False,
        help_text="Newer version that supersedes this contract",
    )

    # ========================================================================
    # CONTRACT METADATA
    # ========================================================================
    contract_number = models.CharField(max_length=100, blank=True, help_text="Provider's contract reference number")

    contract_type = models.CharField(
        max_length=20,
        choices=ContractTypeChoices,
        default=ContractTypeChoices.NEW,
        editable=False,
        help_text="Type of contract (set automatically)",
    )

    # ========================================================================
    # FIXED ATTRIBUTES - Cannot change in amendments
    # ========================================================================
    charge_currency = models.CharField(
        max_length=3,
        choices=CurrencyChoices,
        default=CurrencyChoices.CZK,
        blank=True,
        help_text="Currency for all charges (defaults to CZK if not specified, cannot be changed in amendments)",
    )

    # ========================================================================
    # ATTRIBUTES - copied or changed with each version
    # ========================================================================
    non_recurring_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        default=Decimal("0"),
        help_text="One-time fees for this version (setup, installation, etc.)",
    )

    recurring_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Recurring fee amount (optional for amendments)",
    )

    recurring_charge_period = models.CharField(
        max_length=20,
        choices=RecurringChargePeriodChoices,
        null=True,
        blank=True,
        help_text="Frequency of recurring charges (optional for amendments)",
    )

    number_of_recurring_charges = models.PositiveIntegerField(
        null=True, blank=True, help_text="Number of recurring charge periods in this contract (optional for amendments)"
    )

    start_date = models.DateField(null=True, blank=True, help_text="When this contract version starts (optional)")

    end_date = models.DateField(null=True, blank=True, help_text="When this contract version ends (optional)")

    notes = models.TextField(blank=True, help_text="Notes specific to this version")

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================
    segments = models.ManyToManyField(
        "cesnet_service_path_plugin.Segment",
        through="ContractSegmentMapping",
        related_name="contracts",
        help_text="Network segments covered by this contract",
    )

    # ========================================================================
    # CLONING CONFIGURATION
    # ========================================================================
    clone_fields = [
        "contract_number",
        "charge_currency",
        "non_recurring_charge",
        "recurring_charge",
        "recurring_charge_period",
        "number_of_recurring_charges",
        "start_date",
        "end_date",
        "notes",
        "segments",
    ]

    class Meta:
        ordering = ("contract_number", "end_date")
        verbose_name = "Contract Info"
        verbose_name_plural = "Contract Infos"

    def __str__(self):
        version_info = f"v{self.version}" if self.version > 1 else ""
        contract_id = self.contract_number or f"Contract #{self.pk}"
        return f"{contract_id} {version_info}".strip()

    def get_absolute_url(self):
        return reverse("plugins:cesnet_service_path_plugin:contractinfo", args=[self.pk])

    # ========================================================================
    # VERSION CHAIN PROPERTIES
    # ========================================================================
    @property
    def is_active(self):
        """A contract is active if it's not superseded by a newer version"""
        return self.superseded_by is None

    @property
    def version(self):
        """Calculate version number by counting predecessors in the chain"""
        count = 1
        current = self.previous_version
        while current:
            count += 1
            current = current.previous_version
        return count

    @property
    def next_version(self):
        """Get the next version (if superseded) - alias for superseded_by"""
        return self.superseded_by

    def is_latest_version(self):
        """Check if this is the latest version - alias for is_active"""
        return self.is_active

    def get_first_version(self):
        """Get the first version in the chain (walk backwards)"""
        current = self
        while current.previous_version:
            current = current.previous_version
        return current

    def get_latest_version(self):
        """Get the latest (active) version in the chain (walk forwards)"""
        current = self
        while current.superseded_by:
            current = current.superseded_by
        return current

    def get_version_history(self):
        """
        Get all versions of this contract from oldest to newest.
        Returns a list starting with v1 and ending with the latest version.
        """
        versions = []

        # Go to first version
        current = self.get_first_version()
        versions.append(current)

        # Walk forward collecting all versions
        while current.superseded_by:
            current = current.superseded_by
            versions.append(current)

        return versions

    # ========================================================================
    # COMPUTED FINANCIAL PROPERTIES
    # ========================================================================
    @property
    def commitment_end_date(self):
        """
        Calculate when the commitment period ends based on:
        start_date + (recurring_charge_period × number_of_recurring_charges)
        """
        if not all([self.start_date, self.recurring_charge_period, self.number_of_recurring_charges]):
            return None

        period_map = {
            RecurringChargePeriodChoices.MONTHLY: 1,
            RecurringChargePeriodChoices.QUARTERLY: 3,
            RecurringChargePeriodChoices.SEMI_ANNUALLY: 6,
            RecurringChargePeriodChoices.ANNUALLY: 12,
        }
        total_months = period_map[self.recurring_charge_period] * self.number_of_recurring_charges
        return self.start_date + relativedelta(months=total_months)

    @property
    def total_recurring_cost(self):
        """Calculate total cost of all recurring charges"""
        if self.recurring_charge is None or self.number_of_recurring_charges is None:
            return 0
        return self.recurring_charge * self.number_of_recurring_charges

    @property
    def total_contract_value(self):
        """Total value of this version (recurring + non-recurring)"""
        total = self.total_recurring_cost
        if self.non_recurring_charge:
            total += self.non_recurring_charge
        return total

    # ========================================================================
    # VALIDATION
    # ========================================================================
    def clean(self):
        from django.core.exceptions import ValidationError

        super().clean()

        # Validate date logic
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError({"end_date": "End date cannot be earlier than start date"})

        # Fixed fields cannot change in amendments
        if self.previous_version:
            if self.charge_currency != self.previous_version.charge_currency:
                raise ValidationError({"charge_currency": "Currency cannot be changed in amendments"})

    # ========================================================================
    # CLONING (for creating amendments)
    # ========================================================================
    def clone(self):
        """
        Override clone() method to handle contract versioning.
        Called when the clone button is used in NetBox UI.
        Returns a dictionary of attributes for the cloned instance.

        All standard fields are cloned via clone_fields.
        This method only handles special version chain setup.
        """
        # Get all cloned attributes from clone_fields
        # This includes: contract_number, charges, dates, notes, segments
        attrs = super().clone()

        # Set up versioning fields (special handling for version chain)
        # Use self.pk so it can be parsed correctly by the view
        attrs["previous_version"] = self.pk
        attrs["superseded_by"] = None
        attrs["contract_type"] = ContractTypeChoices.AMENDMENT

        return attrs

    def save(self, *args, **kwargs):
        """Override save to handle version chain updates and cumulative notes"""
        is_new = self.pk is None

        # Auto-set contract_type based on previous_version
        if is_new and self.previous_version:
            # If contract_type is still default (NEW) but we have a previous_version, it's an AMENDMENT
            # (unless explicitly set to RENEWAL, which is preserved)
            if self.contract_type == ContractTypeChoices.NEW:
                self.contract_type = ContractTypeChoices.AMENDMENT
            # Validate that contract_type is appropriate for a versioned contract
            elif self.contract_type not in [ContractTypeChoices.AMENDMENT, ContractTypeChoices.RENEWAL]:
                self.contract_type = ContractTypeChoices.AMENDMENT

        # If this is a new version, we need to update previous version after save
        update_previous = is_new and self.previous_version and not self.previous_version.superseded_by

        super().save(*args, **kwargs)

        # Update previous version's superseded_by link
        if update_previous:
            self.previous_version.superseded_by = self
            self.previous_version.save(update_fields=["superseded_by"])

    # ========================================================================
    # HELPER METHODS FOR UI
    # ========================================================================
    def get_status_color(self):
        """Get color for status badge in UI"""
        if self.is_active:
            # Check if contract is still valid
            today = timezone.now().date()
            if self.end_date and self.end_date < today:
                return "danger"  # Expired
            elif self.start_date > today:
                return "info"  # Future
            else:
                return "success"  # Active
        else:
            return "secondary"  # Superseded

    def get_contract_type_color(self):
        """Get color for contract type badge"""
        return ContractTypeChoices.colors.get(self.contract_type, "gray")

    def get_currency_color(self):
        """Get color for currency badge"""
        return CurrencyChoices.colors.get(self.charge_currency, "gray")

    def get_commitment_status(self):
        """Get commitment period status"""
        if not self.end_date:
            return None

        today = timezone.now().date()

        if self.end_date < today:
            return {"color": "success", "status": "Commitment ended", "days": (today - self.end_date).days}
        else:
            days_remaining = (self.end_date - today).days
            if days_remaining <= 30:
                color = "warning"
            else:
                color = "info"

            return {"color": color, "status": "In commitment", "days": days_remaining}

    def get_end_date_color(self):
        """
        Color code the contract end date based on proximity to current date.
        Red - 30+ days to the end
        Orange - within 30 days
        Green - the end date already passed
        Gray - no end date set.
        """
        if not self.end_date:
            return "secondary"

        today = timezone.now().date()
        end_date = self.end_date

        if end_date < today:
            return "success"
        elif (end_date - today).days <= 30:
            return "warning"
        else:
            return "danger"

    def get_end_date_tooltip(self):
        """Generate tooltip text for contract end date."""
        if not self.end_date:
            return "No contract end date set."

        end_date = self.end_date
        today = timezone.now().date()

        if end_date < today:
            return f"Contract ended on {end_date}."
        else:
            days_remaining = (end_date - today).days
            return f"Contract ends on {end_date} ({days_remaining} days remaining)."

    def get_commitment_end_date_color(self):
        """
        Color code the commitment end date based on proximity to current date.
        Red - 30+ days to the end
        Orange - within 30 days
        Green - the commitment already passed
        Gray - no commitment period calculated.
        """
        if not self.commitment_end_date:
            return "secondary"

        today = timezone.now().date()
        commitment_date = self.commitment_end_date

        if commitment_date < today:
            return "success"
        elif (commitment_date - today).days <= 30:
            return "warning"
        else:
            return "danger"

    def get_commitment_end_date_tooltip(self):
        """Generate tooltip text for commitment end date (based on recurring charges)."""
        if not self.commitment_end_date:
            return "No commitment period calculated (insufficient payment schedule data)."

        commitment_date = self.commitment_end_date
        today = timezone.now().date()

        if commitment_date < today:
            return f"Commitment period ended on {commitment_date}."
        else:
            days_remaining = (commitment_date - today).days
            return f"Commitment period ends on {commitment_date} ({days_remaining} days remaining)."


class ContractSegmentMapping(models.Model):
    """
    Through model for ContractInfo-Segment M:N relationship.
    Allows tracking when segments were added/removed from contracts.
    """

    contract = models.ForeignKey(ContractInfo, on_delete=models.CASCADE)
    segment = models.ForeignKey("cesnet_service_path_plugin.Segment", on_delete=models.CASCADE)

    added_date = models.DateField(auto_now_add=True, help_text="When this segment was added to the contract")

    notes = models.TextField(blank=True, help_text="Notes about this segment-contract relationship")

    class Meta:
        unique_together = ("contract", "segment")
        ordering = ("contract", "segment")
        verbose_name = "Contract-Segment Mapping"
        verbose_name_plural = "Contract-Segment Mappings"

    def __str__(self):
        return f"{self.contract} → {self.segment}"
