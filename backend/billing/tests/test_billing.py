from decimal import Decimal

from billing.models import Invoice, Subscription


def test_onboarding_with_packages_creates_one_invoice(
    api,
    admin,
    packages,
    login,
):
    login(admin, "AdminPass!2345")

    response = api.post(
        "/api/v1/users/",
        {
            "email": "ada@isp.test",
            "full_name": "Ada Customer",
            "password": "Customer!2345",
            "package_ids": [packages[0].id, packages[1].id],
        },
        format="json",
    )

    assert response.status_code == 201, response.content

    invoice = response.data["invoice"]

    assert invoice is not None
    assert Decimal(invoice["total_amount"]) == Decimal("1300.00")
    assert len(invoice["items"]) == 2
    assert Invoice.objects.count() == 1


def test_onboarding_without_packages_creates_no_invoice(
    api,
    admin,
    login,
):
    login(admin, "AdminPass!2345")

    response = api.post(
        "/api/v1/users/",
        {
            "email": "bob@isp.test",
            "full_name": "Bob",
            "password": "Customer!2345",
        },
        format="json",
    )

    assert response.status_code == 201, response.content
    assert response.data["invoice"] is None
    assert Invoice.objects.count() == 0


def test_later_assign_invoices_only_new_packages(
    api,
    admin,
    customer,
    packages,
    login,
):
    login(admin, "AdminPass!2345")

    first = api.post(
        "/api/v1/subscriptions/",
        {
            "user": customer.id,
            "package_ids": [packages[0].id],
        },
        format="json",
    )

    assert first.status_code == 201, first.content

    second = api.post(
        "/api/v1/subscriptions/",
        {
            "user": customer.id,
            "package_ids": [packages[1].id],
        },
        format="json",
    )

    assert second.status_code == 201, second.content
    assert Decimal(second.data["invoice"]["total_amount"]) == Decimal(
        "300.00"
    )
    assert Invoice.objects.filter(user=customer).count() == 2


def test_cancel_does_not_create_invoice(
    api,
    admin,
    customer,
    packages,
    login,
):
    login(admin, "AdminPass!2345")

    assigned = api.post(
        "/api/v1/subscriptions/",
        {
            "user": customer.id,
            "package_ids": [packages[0].id],
        },
        format="json",
    )

    assert assigned.status_code == 201, assigned.content

    subscription_id = assigned.data["subscriptions"][0]["id"]

    cancel = api.patch(
        f"/api/v1/subscriptions/{subscription_id}/",
        {"status": Subscription.Status.CANCELLED},
        format="json",
    )

    assert cancel.status_code == 200, cancel.content
    assert cancel.data["status"] == Subscription.Status.CANCELLED
    assert Invoice.objects.count() == 1


def test_inactive_package_cannot_be_assigned(
    api,
    admin,
    customer,
    packages,
    login,
):
    login(admin, "AdminPass!2345")

    response = api.post(
        "/api/v1/subscriptions/",
        {
            "user": customer.id,
            "package_ids": [packages[2].id],
        },
        format="json",
    )

    assert response.status_code == 400


def test_duplicate_active_assignment_is_rejected(
    api,
    admin,
    customer,
    packages,
    login,
):
    login(admin, "AdminPass!2345")

    first = api.post(
        "/api/v1/subscriptions/",
        {
            "user": customer.id,
            "package_ids": [packages[0].id],
        },
        format="json",
    )

    assert first.status_code == 201, first.content

    second = api.post(
        "/api/v1/subscriptions/",
        {
            "user": customer.id,
            "package_ids": [packages[0].id],
        },
        format="json",
    )

    assert second.status_code == 400


def test_invoices_are_read_only(
    api,
    admin,
    customer,
    packages,
    login,
):
    login(admin, "AdminPass!2345")

    created = api.post(
        "/api/v1/subscriptions/",
        {
            "user": customer.id,
            "package_ids": [packages[0].id],
        },
        format="json",
    )

    assert created.status_code == 201, created.content

    invoice_id = created.data["invoice"]["id"]

    patched = api.patch(
        f"/api/v1/invoices/{invoice_id}/",
        {"total_amount": "1.00"},
        format="json",
    )

    assert patched.status_code == 405

    deleted = api.delete(
        f"/api/v1/invoices/{invoice_id}/"
    )

    assert deleted.status_code == 405


def test_user_cannot_see_another_users_invoices(
    api,
    admin,
    customer,
    other_customer,
    packages,
    login,
):
    login(admin, "AdminPass!2345")

    customer_invoice = api.post(
        "/api/v1/subscriptions/",
        {
            "user": customer.id,
            "package_ids": [packages[0].id],
        },
        format="json",
    )

    assert customer_invoice.status_code == 201

    other_invoice = api.post(
        "/api/v1/subscriptions/",
        {
            "user": other_customer.id,
            "package_ids": [packages[1].id],
        },
        format="json",
    )

    assert other_invoice.status_code == 201

    api.credentials()
    login(customer, "Customer!2345")

    listing = api.get("/api/v1/invoices/")

    assert listing.status_code == 200

    results = listing.data["results"]

    assert len(results) == 1
    assert results[0]["user"] == customer.id

    other_invoice_id = Invoice.objects.get(
        user=other_customer
    ).id

    forbidden = api.get(
        f"/api/v1/invoices/{other_invoice_id}/"
    )

    assert forbidden.status_code == 404