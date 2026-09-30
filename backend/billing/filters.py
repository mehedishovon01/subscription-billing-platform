import django_filters
from .models import Invoice, Package, Subscription


class PackageFilter(django_filters.FilterSet):
    class Meta:
        model = Package
        fields = ("type", "is_active")


class SubscriptionFilter(django_filters.FilterSet):
    class Meta:
        model = Subscription
        fields = ("user", "status", "package")


class InvoiceFilter(django_filters.FilterSet):
    created_after = django_filters.IsoDateTimeFilter(
        field_name="created_at",
        lookup_expr="gte"
    )
    created_before = django_filters.IsoDateTimeFilter(
        field_name="created_at",
        lookup_expr="lte"
    )

    class Meta:
        model = Invoice
        fields = ("user",)
