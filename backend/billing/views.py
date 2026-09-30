from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .filters import InvoiceFilter, PackageFilter, SubscriptionFilter
from .models import Invoice, Package, Subscription
from .serializers import (
    AssignSubscriptionsSerializer,
    InvoiceSerializer,
    PackageSerializer,
    SubscriptionSerializer,
    SubscriptionUpdateSerializer,
)


class IsAdminOrReadOwn(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user.is_staff)


class PackageListCreateView(generics.ListCreateAPIView):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [permissions.IsAdminUser]
    filterset_class = PackageFilter
    search_fields = ("name",)
    ordering_fields = ("name", "price", "created_at")
    http_method_names = ["get", "post", "head", "options"]


class PackageDetailView(generics.RetrieveUpdateAPIView):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ["get", "patch", "head", "options"]


class SubscriptionListCreateView(generics.ListCreateAPIView):
    queryset = Subscription.objects.none()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAdminOrReadOwn]
    filterset_class = SubscriptionFilter
    search_fields = ("user__email", "user__full_name", "package__name", "package__type")
    ordering_fields = ("assigned_at",)
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        qs = Subscription.objects.select_related("user", "package")
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = AssignSubscriptionsSerializer(
            data=request.data,
            context={
                "request": request
            }
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(
            {
                "subscriptions": SubscriptionSerializer(
                    result["subscriptions"],
                    many=True
                ).data,
                "invoice": (
                    InvoiceSerializer(result["invoice"]).data
                    if result["invoice"] is not None
                    else None
                ),
            },
            status=status.HTTP_201_CREATED,
        )


class SubscriptionDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAdminOrReadOwn]
    http_method_names = ["get", "patch", "head", "options"]

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return SubscriptionUpdateSerializer
        return SubscriptionSerializer

    def get_queryset(self):
        qs = Subscription.objects.select_related(
            "user", "package"
        )
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        data = SubscriptionSerializer(updated).data
        invoice = getattr(updated, "generated_invoice", None)
        data["invoice"] = InvoiceSerializer(invoice).data if invoice else None
        return Response(data)


class InvoiceListView(generics.ListAPIView):
    queryset = Invoice.objects.none()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = InvoiceFilter
    search_fields = ("invoice_number", "user__email", "user__full_name", "items__package_name")
    ordering_fields = ("created_at", "total_amount")

    def get_queryset(self):
        qs = Invoice.objects.select_related(
            "user"
        ).prefetch_related("items")
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)


class InvoiceDetailView(generics.RetrieveAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Invoice.objects.select_related(
            "user"
        ).prefetch_related("items")
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)
