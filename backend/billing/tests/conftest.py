import pytest
from rest_framework.test import APIClient

from accounts.models import User
from billing.models import Package


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def admin(db):
    return User.objects.create_superuser(
        email="admin@isp.test",
        password="AdminPass!2345",
        full_name="Admin User",
    )


@pytest.fixture
def customer(db):
    return User.objects.create_user(
        email="customer@isp.test",
        password="Customer!2345",
        full_name="Customer User",
    )


@pytest.fixture
def other_customer(db):
    return User.objects.create_user(
        email="other@isp.test",
        password="Customer!2345",
        full_name="Other User",
    )


@pytest.fixture
def packages(db):
    return [
        Package.objects.create(
            name="Fiber 50",
            type=Package.Type.ISP,
            price="1000.00",
        ),
        Package.objects.create(
            name="Real IP",
            type=Package.Type.REAL_IP,
            price="300.00",
        ),
        Package.objects.create(
            name="Old TV",
            type=Package.Type.TV,
            price="200.00",
            is_active=False,
        ),
    ]


@pytest.fixture
def login(api):
    def _login(user, password):
        response = api.post(
            "/api/v1/auth/login/",
            {
                "email": user.email,
                "password": password,
            },
            format="json",
        )

        assert response.status_code == 200, response.content

        api.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
        )

        return response.data

    return _login