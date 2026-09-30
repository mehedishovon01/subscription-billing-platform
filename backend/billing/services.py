from decimal import Decimal

from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from accounts.models import User
from .models import Invoice, InvoiceItem, Package, Subscription


@transaction.atomic
def assign_packages(*, user, package_ids, created_by=None):
    """Assign packages and invoice only those newly assigned."""
    ids = list(dict.fromkeys(package_ids))
    if not ids:
        raise ValidationError({"package_ids": ["Select at least one package."]})

    # Serialize package assignments for this customer on PostgreSQL.
    user = User.objects.select_for_update().get(pk=user.pk)
    packages = list(
        Package.objects.select_for_update()
        .filter(id__in=ids)
        .order_by("id")
    )
    if len(packages) != len(ids):
        raise ValidationError({
            "package_ids": ["One or more packages were not found."]
        })

    inactive = [pkg.name for pkg in packages if not pkg.is_active]
    if inactive:
        raise ValidationError({
            "package_ids": [
                f"Inactive packages cannot be assigned: {', '.join(inactive)}."
            ]
        })

    existing_package_ids = set(
        Subscription.objects.filter(
            user=user,
            status=Subscription.Status.ACTIVE,
            package_id__in=ids,
        ).values_list("package_id", flat=True)
    )
    new_packages = [
        package for package in packages
        if package.id not in existing_package_ids
    ]

    if not new_packages:
        raise ValidationError({
            "package_ids": ["All requested packages are already assigned to this user."],
        })

    try:
        # Keep the unique constraint as a final guard against concurrent writes.
        with transaction.atomic():
            subscriptions = [
                Subscription.objects.create(
                    user=user,
                    package=package,
                    created_by=created_by,
                )
                for package in new_packages
            ]
            invoice = (
                create_invoice(
                    user=user,
                    packages=new_packages,
                    created_by=created_by,
                )
                if new_packages
                else None
            )
    except IntegrityError:
        duplicate_exists = Subscription.objects.filter(
            user=user,
            package_id__in=[pkg.id for pkg in new_packages],
            status=Subscription.Status.ACTIVE,
        ).exists()
        if duplicate_exists:
            raise ValidationError({
                "package_ids": [
                    "One or more packages are already assigned to this user."
                ]
            })
        raise

    return subscriptions, invoice


@transaction.atomic
def update_subscription(*, subscription, user, package, status, updated_by=None):
    """Update an assignment and invoice its newly assigned active package."""
    current = Subscription.objects.select_for_update().get(pk=subscription.pk)
    affected_user_ids = sorted({current.user_id, user.pk})
    locked_users = {
        item.pk: item
        for item in User.objects.select_for_update()
        .filter(pk__in=affected_user_ids)
        .order_by("pk")
    }
    user = locked_users[user.pk]
    package = Package.objects.select_for_update().get(pk=package.pk)

    assignment_changed = (
        current.user_id != user.pk or current.package_id != package.pk
    )
    becoming_active = (
        current.status != Subscription.Status.ACTIVE
        and status == Subscription.Status.ACTIVE
    )
    if assignment_changed and status != Subscription.Status.ACTIVE:
        raise ValidationError({
            "status": "Change the subscription while it is active to create an assignment invoice."
        })

    should_invoice = (
        status == Subscription.Status.ACTIVE
        and (assignment_changed or becoming_active)
    )
    if should_invoice and not package.is_active:
        raise ValidationError({
            "package": "Inactive packages cannot be assigned."
        })

    duplicate = Subscription.objects.filter(
        user=user,
        package=package,
        status=Subscription.Status.ACTIVE,
    ).exclude(pk=current.pk).exists()
    if status == Subscription.Status.ACTIVE and duplicate:
        raise ValidationError({
            "package": "User already has subscription for this package."
        })

    current.user = user
    current.package = package
    current.status = status
    if assignment_changed or becoming_active:
        current.assigned_at = timezone.now()
    if status == Subscription.Status.CANCELLED:
        if current.cancelled_at is None:
            current.cancelled_at = timezone.now()
    else:
        current.cancelled_at = None

    try:
        with transaction.atomic():
            current.save(update_fields=[
                "user", "package", "status", "cancelled_at", "assigned_at"
            ])
            invoice = (
                create_invoice(
                    user=user,
                    packages=[package],
                    created_by=updated_by,
                )
                if should_invoice
                else None
            )
    except IntegrityError:
        duplicate = Subscription.objects.filter(
            user=user,
            package=package,
            status=Subscription.Status.ACTIVE,
        ).exclude(pk=current.pk).exists()
        if duplicate:
            raise ValidationError({
                "package": "User already has an active subscription for this package."
            })
        raise

    return current, invoice


def create_invoice(*, user, packages, created_by=None):
    total = sum((pkg.price for pkg in packages), Decimal("0.00"))
    invoice = Invoice.objects.create(
        user=user,
        total_amount=total,
        created_by=created_by,
    )
    InvoiceItem.objects.bulk_create([
        InvoiceItem(
            invoice=invoice,
            package=pkg,
            package_name=pkg.name,
            package_type=pkg.type,
            unit_price=pkg.price,
        )
        for pkg in packages
    ])
    return invoice
