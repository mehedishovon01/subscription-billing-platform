def test_login_refresh_and_logout_blacklists_refresh(
    api,
    admin,
    login,
):
    tokens = login(admin, "AdminPass!2345")
    refresh = tokens["refresh"]

    logout = api.post(
        "/api/v1/auth/logout/",
        {"refresh": refresh},
        format="json",
    )

    assert logout.status_code == 204, logout.content

    response = api.post(
        "/api/v1/auth/refresh/",
        {"refresh": refresh},
        format="json",
    )

    assert response.status_code == 401, response.content


def test_user_cannot_register(
    api,
    customer,
    login,
):
    login(customer, "Customer!2345")

    response = api.post(
        "/api/v1/users/",
        {
            "email": "new@isp.test",
            "full_name": "New",
            "password": "Customer!2345",
        },
        format="json",
    )

    assert response.status_code == 403, response.content