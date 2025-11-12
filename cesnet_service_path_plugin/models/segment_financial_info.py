from django.db import models
from django.conf import settings
from django.urls import reverse
from netbox.models import NetBoxModel
from django.utils import timezone
from dateutil.relativedelta import relativedelta


def get_currency_choices():
    """Get currency choices from plugin configuration."""
    config = settings.PLUGINS_CONFIG.get("netbox_cesnet_service_path_plugin", {})
    return config.get(
        "currencies",
        [
            ("CZK", "Czech Koruna"),
            ("EUR", "Euro"),
            ("USD", "US Dollar"),
        ],
    )


def get_default_currency():
    """Get default currency from plugin configuration."""
    config = settings.PLUGINS_CONFIG.get("netbox_cesnet_service_path_plugin", {})
    return config.get("default_currency", "CZK")


class SegmentFinancialInfo(NetBoxModel):
    segment = models.OneToOneField(
        "cesnet_service_path_plugin.Segment", on_delete=models.CASCADE, related_name="financial_info"
    )

    monthly_charge = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Fixed monthly fee for the service lease"
    )

    charge_currency = models.CharField(
        max_length=3,
        choices=get_currency_choices,
        help_text="Currency for all charges",
    )

    non_recurring_charge = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, help_text="One-time setup or installation fee"
    )

    commitment_period_months = models.PositiveIntegerField(
        blank=True, null=True, help_text="Number of months the contract cannot be terminated"
    )

    notes = models.TextField(blank=True, help_text="Additional financial notes")

    class Meta:
        ordering = ("segment",)

    def __str__(self):
        return f"{self.segment.name} - Financial Info"

    def get_absolute_url(self):
        return reverse("plugins:cesnet_service_path_plugin:segmentfinancialinfo", args=[self.pk])

    @property
    def total_commitment_cost(self):
        """Calculate total cost over commitment period."""
        if self.commitment_period_months and self.monthly_charge:
            return self.commitment_period_months * self.monthly_charge
        return None

    @property
    def total_cost_including_setup(self):
        """Total cost including non-recurring charge."""
        from decimal import Decimal

        total = self.total_commitment_cost or Decimal("0")
        if self.non_recurring_charge:
            total += self.non_recurring_charge
        return total if total > 0 else None

    @property
    def commitment_end_date(self):
        """Calculate the end date of the commitment period."""

        if self.commitment_period_months and self.segment.install_date:
            start_date = self.segment.install_date
            end_date = start_date + relativedelta(months=self.commitment_period_months)
            return end_date
        return None

    def get_commitment_end_date_color(self):
        """
        Color code the commitment end date based on proximity to current date.
        Red - 30+ days to the end
        Orange - within 30 days
        Green - the end date already passed
        Gray - no commitment.
        """

        if not self.commitment_end_date:
            return "gray"

        today = timezone.now().date()
        end_date = self.commitment_end_date

        if end_date < today:
            return "green"
        elif (end_date - today).days <= 30:
            return "orange"
        else:
            return "red"

    def get_commitment_end_date_tooltip(self):
        """Generate tooltip text for commitment end date."""
        if not self.commitment_end_date:
            return "No commitment period set."

        end_date = self.commitment_end_date
        today = timezone.now().date()

        if end_date < today:
            return f"Commitment period ended on {end_date}."
        else:
            days_remaining = (end_date - today).days
            return f"Commitment period ends on {end_date} ({days_remaining} days remaining)."
