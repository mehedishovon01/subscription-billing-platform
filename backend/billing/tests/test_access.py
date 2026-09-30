def test_unauthenticated_is_401(api, db):
    response = api.get("/api/v1/invoices/")

    assert response.status_code == 401


def test_customer_cannot_create_subscription(
    api,
    customer,
    packages,
    login,
):
    login(customer, "Customer!2345")

    response = api.post(
        "/api/v1/subscriptions/",
        {
            "user": customer.id,
            "package_ids": [packages[0].id],
        },
        format="json",
    )

    assert response.status_code == 403


def test_customer_cannot_cancel_subscription(
    api,
    admin,
    customer,
    packages,
    login,
):
    # Create a subscription as admin first.
    login(admin, "AdminPass!2345")

    response = api.post(
        "/api/v1/subscriptions/",
        {
            "user": customer.id,
            "package_ids": [packages[0].id],
        },
        format="json",
    )

    assert response.status_code == 201, response.content

    subscription_id = response.data["subscriptions"][0]["id"]

    # Switch to customer.
    api.credentials()
    login(customer, "Customer!2345")

    response = api.patch(
        f"/api/v1/subscriptions/{subscription_id}/",
        {"status": "cancelled"},
        format="json",
    )

    assert response.status_code == 403


def test_customer_cannot_access_other_customer_subscription(
    api,
    admin,
    customer,
    other_customer,
    packages,
    login,
):
    # Create subscription for another customer as admin.
    login(admin, "AdminPass!2345")

    response = api.post(
        "/api/v1/subscriptions/",
        {
            "user": other_customer.id,
            "package_ids": [packages[0].id],
        },
        format="json",
    )

    assert response.status_code == 201, response.content

    subscription_id = response.data["subscriptions"][0]["id"]

    # Login as customer.
    api.credentials()
    login(customer, "Customer!2345")

    response = api.get(
        f"/api/v1/subscriptions/{subscription_id}/"
    )

    assert response.status_code in (403, 404)


def test_customer_cannot_access_other_customer_invoice(
    api,
    admin,
    customer,
    other_customer,
    packages,
    login,
):
    # Create subscription/invoice for another customer.
    login(admin, "AdminPass!2345")

    response = api.post(
        "/api/v1/subscriptions/",
        {
            "user": other_customer.id,
            "package_ids": [packages[0].id],
        },
        format="json",
    )

    assert response.status_code == 201, response.content

    invoice_id = response.data["invoice"]["id"]

    # Login as customer.
    api.credentials()
    login(customer, "Customer!2345")

    response = api.get(
        f"/api/v1/invoices/{invoice_id}/"
    )

    assert response.status_code in (403, 404)