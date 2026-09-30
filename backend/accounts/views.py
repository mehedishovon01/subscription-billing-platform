from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .models import User
from .serializers import (
    LogoutSerializer, MeSerializer, OnboardUserSerializer,
    UserSerializer, UserUpdateSerializer
)


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["post", "options"]

    @extend_schema(responses={204: None})
    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response(
                {"refresh": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh)
            token.blacklist()
        except TokenError:
            return Response(
                {"refresh": ["Token is invalid or expired."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = MeSerializer
    http_method_names = ["get", "patch", "head", "options"]

    def get_object(self):
        return self.request.user


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ("is_staff", "is_active")
    search_fields = ("email", "full_name")
    ordering_fields = ("date_joined", "email")
    http_method_names = ["get", "post", "head", "options"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OnboardUserSerializer
        return UserSerializer


class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ["get", "patch", "head", "options"]

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return UserUpdateSerializer
        return UserSerializer
