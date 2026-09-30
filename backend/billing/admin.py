from django.contrib import admin
from .models import Invoice, InvoiceItem, Package, Subscription


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = (
        "name", "type", "price", "is_active"
    )
    list_filter = (
        "type", "is_active"
    )
    search_fields = (
        "name",
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "user", "package", "status", "assigned_at"
    )
    list_filter = (
        "status",
    )


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    can_delete = False
    readonly_fields = (
        "package", "package_name", "package_type", "unit_price"
    )

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number", "user", "total_amount", "created_at"
    )
    inlines = [InvoiceItemInline]
    readonly_fields = (
        "user", "invoice_number", "total_amount", "created_at", "created_by"
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
