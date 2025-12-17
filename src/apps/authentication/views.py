from django.contrib.auth import authenticate
from django.utils import timezone

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from apps.authentication.serializer import LoginSerializer, RegisterSerializer


class UserAuthAPIView(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=["post"])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "User created successfully"},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = authenticate(
            request=request,
            email=data["email"],
            password=data["password"],
        )

        if not user:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        refresh = RefreshToken.for_user(user)

        user.last_login_time = timezone.now()
        user.last_login_ip = (
            request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0]
            or request.META.get("REMOTE_ADDR")
        )
        user.last_login_uagent = request.META.get("HTTP_USER_AGENT", "")

        user.save(
            update_fields=[
                "last_login_time",
                "last_login_ip",
                "last_login_uagent",
            ]
        )

        return Response(
            {
                "message": "Login successful",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )
