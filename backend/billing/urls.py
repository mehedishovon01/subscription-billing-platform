from django.urls import path
from .views import (
    InvoiceDetailView,
    InvoiceListView,
    PackageDetailView,
    PackageListCreateView,
    SubscriptionDetailView,
    SubscriptionListCreateView,
)

urlpatterns = [
    path("packages/", PackageListCreateView.as_view(), name="package-list"),
    path("packages/<int:pk>/", PackageDetailView.as_view(), name="package-detail"),
    path("subscriptions/", SubscriptionListCreateView.as_view(), name="subscription-list"),
    path("subscriptions/<int:pk>/", SubscriptionDetailView.as_view(), name="subscription-detail"),
    path("invoices/", InvoiceListView.as_view(), name="invoice-list"),
    path("invoices/<int:pk>/", InvoiceDetailView.as_view(), name="invoice-detail"),
]
