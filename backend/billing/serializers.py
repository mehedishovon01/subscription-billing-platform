from rest_framework import serializers
from accounts.models import User
from .models import Invoice, InvoiceItem, Package, Subscription
from .services import assign_packages, update_subscription


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = (
            "id", "name", "type", "price", "is_active",
            "created_at", "updated_at"
        )
        read_only_fields = (
            "id", "created_at", "updated_at"
        )


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = (
            "id", "package", "package_name",
            "package_type", "unit_price"
        )
        read_only_fields = fields


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(
        many=True,
        read_only=True
    )
    user_email = serializers.EmailField(
        source="user.email",
        read_only=True
    )
    user_full_name = serializers.CharField(
        source="user.full_name",
        read_only=True
    )

    class Meta:
        model = Invoice
        fields = (
            "id", "invoice_number", "user", "user_email",
            "user_full_name", "items", "total_amount",
            "created_at",
        )
        read_only_fields = fields


class SubscriptionSerializer(serializers.ModelSerializer):
    package = PackageSerializer(
        read_only=True
    )
    user_email = serializers.EmailField(
        source="user.email",
        read_only=True
    )
    user_full_name = serializers.CharField(
        source="user.full_name",
        read_only=True
    )

    class Meta:
        model = Subscription
        fields = (
            "id", "user", "user_email", "user_full_name",
            "package", "status", "assigned_at",
            "cancelled_at",
        )
        read_only_fields = fields


class SubscriptionUpdateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False
    )
    package = serializers.PrimaryKeyRelatedField(
        queryset=Package.objects.all(),
        required=False
    )
    package_id = serializers.PrimaryKeyRelatedField(
        source="package",
        queryset=Package.objects.all(),
        required=False,
        write_only=True
    )

    class Meta:
        model = Subscription
        fields = (
            "user", "package", "package_id", "status"
        )
        validators = []

    def validate(self, attrs):
        instance = self.instance
        user = attrs.get("user", instance.user)
        package = attrs.get("package", instance.package)
        status = attrs.get("status", instance.status)
        package_changed = package.pk != instance.package_id
        if not package.is_active and (
            package_changed or status == Subscription.Status.ACTIVE
        ):
            raise serializers.ValidationError({
                "package": "Inactive packages cannot be assigned."
            })
        if (
            status == Subscription.Status.ACTIVE
            and Subscription.objects.filter(
                user=user,
                package=package,
                status=Subscription.Status.ACTIVE,
            )
            .exclude(pk=instance.pk)
            .exists()
        ):
            raise serializers.ValidationError(
                {
                    "package": "User already has subscription for this package"
                }
            )
        return attrs

    def update(self, instance, validated_data):
        request = self.context["request"]
        instance, invoice = update_subscription(
            subscription=instance,
            user=validated_data.get("user", instance.user),
            package=validated_data.get("package", instance.package),
            status=validated_data.get("status", instance.status),
            updated_by=request.user,
        )
        instance.generated_invoice = invoice
        return instance


class AssignSubscriptionsSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    package_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
    )

    def create(self, validated_data):
        subscriptions, invoice = assign_packages(
            user=validated_data["user"],
            package_ids=validated_data["package_ids"],
            created_by=self.context["request"].user,
        )
        return {
            "subscriptions": subscriptions,
            "invoice": invoice
        }
