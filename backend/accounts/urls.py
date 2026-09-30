from django.urls import path
from .views import (
    LogoutView, MeView, UserDetailView, UserListCreateView
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView
)


urlpatterns = [
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/logout/", LogoutView.as_view(), name="token_logout"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("users/", UserListCreateView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
]
