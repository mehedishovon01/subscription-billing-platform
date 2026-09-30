from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from billing.models import Package
from billing.serializers import InvoiceSerializer
from billing.services import assign_packages
from .models import User


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    is_admin = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id", "email", "full_name", "phone", "address",
            "is_staff", "is_admin", "is_active",
            "date_joined",
        )
        read_only_fields = (
            "id", "date_joined", "is_staff"
        )


class MeSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = (
            "id", "date_joined", "is_staff", "is_active", "email"
        )


class OnboardUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    package_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        default=list,
        write_only=True,
    )
    invoice = InvoiceSerializer(read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = (
            "id", "email", "full_name", "phone", "address",
            "password", "package_ids", "invoice", "is_staff",
            "is_active", "date_joined",
        )
        read_only_fields = (
            "id", "is_staff", "date_joined"
        )

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_package_ids(self, value):
        ids = list(dict.fromkeys(value))
        if not ids:
            return ids
        found = set(
            Package.objects.filter(id__in=ids).values_list(
                "id", flat=True
            )
        )
        missing = [
            pkg_id for pkg_id in ids if pkg_id not in found
        ]
        if missing:
            raise serializers.ValidationError(
                f"Unknown package ids: {missing}"
            )
        return ids

    @transaction.atomic
    def create(self, validated_data):
        package_ids = validated_data.pop("package_ids", [])
        password = validated_data.pop("password")
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        invoice = None
        if package_ids:
            _subs, invoice = assign_packages(
                user=user,
                package_ids=package_ids,
                created_by=self.context["request"].user,
            )
        user.invoice = invoice
        return user


class UserUpdateSerializer(UserSerializer):
    password = serializers.CharField(
        write_only=True,
        required=False,
        min_length=8
    )

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ("password",)

    def validate_password(self, value):
        validate_password(value)
        return value

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        instance = super().update(instance, validated_data)
        if password:
            instance.set_password(password)
            instance.save(update_fields=["password"])
        return instance
