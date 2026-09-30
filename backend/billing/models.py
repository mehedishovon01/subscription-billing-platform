import uuid
from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone


class ImmutableQuerySet(models.QuerySet):
    def update(self, **kwargs):
        # Keep SET_NULL cleanup of the optional invoice creator functional.
        if (
            self.model.__name__ == "Invoice"
            and set(kwargs) == {"created_by"}
            and kwargs["created_by"] is None
        ):
            return super().update(**kwargs)
        raise ValueError("Financial records cannot be updated.")

    def delete(self):
        raise ValueError("Financial records cannot be deleted.")


class ImmutableManager(models.Manager.from_queryset(ImmutableQuerySet)):
    pass


class Package(models.Model):
    class Type(models.TextChoices):
        ISP = "isp", "ISP"
        REAL_IP = "realip", "Real IP"
        TV = "tv", "TV"

    name = models.CharField(max_length=120)
    type = models.CharField(
        max_length=16,
        choices=Type.choices,
        db_index=True
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name", "id")
        constraints = [
            models.UniqueConstraint(
                fields=["name", "type"],
                name="uniq_package_name_per_type"
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class Subscription(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    package = models.ForeignKey(
        Package,
        on_delete=models.PROTECT,
        related_name="subscriptions",
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )
    assigned_at = models.DateTimeField(
        default=timezone.now,
        db_index=True
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_subscriptions",
    )

    class Meta:
        ordering = ("-assigned_at", "-id")
        constraints = [
            models.UniqueConstraint(
                fields=["user", "package"],
                condition=Q(status="active"),
                name="uniq_active_subscription_per_user_package",
            ),
        ]

    def __str__(self):
        return f"{self.user_id}:{self.package_id} ({self.status})"

    def cancel(self):
        if self.status == self.Status.CANCELLED:
            return self
        self.status = self.Status.CANCELLED
        self.cancelled_at = timezone.now()
        self.save(update_fields=["status", "cancelled_at"])
        return self


def generate_invoice_number():
    return f"INV-{timezone.now():%Y%m}-{uuid.uuid4().hex[:8].upper()}"


class Invoice(models.Model):
    objects = ImmutableManager()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="invoices",
    )
    invoice_number = models.CharField(
        max_length=32,
        unique=True,
        editable=False,
        default=generate_invoice_number,
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_invoices",
    )

    class Meta:
        ordering = ("-created_at", "-id")

    def __str__(self):
        return self.invoice_number

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValueError("Invoices are immutable and cannot be updated.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Invoices are immutable and cannot be deleted.")


class InvoiceItem(models.Model):
    objects = ImmutableManager()

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.PROTECT,
        related_name="items"
    )
    package = models.ForeignKey(
        Package,
        on_delete=models.PROTECT,
        related_name="invoice_items",
    )
    package_name = models.CharField(max_length=120)
    package_type = models.CharField(max_length=16)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ("id",)

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValueError("Invoice items are immutable and cannot be updated.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Invoice items are immutable and cannot be deleted.")

    def __str__(self):
        return f"{self.package_name} @ {self.unit_price}"
