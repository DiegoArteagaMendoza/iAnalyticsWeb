"""Inicio y cierre de sesión del panel de administración (frontend /panel/)."""
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import update_last_login
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, serializers, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(trim_whitespace=False, write_only=True)


def user_payload(user):
    return {
        "username": user.username,
        "email": user.email,
        "full_name": user.get_full_name() or user.username,
        "is_superuser": user.is_superuser,
    }


class LoginView(APIView):
    """
    Entrega un token nuevo a un usuario del staff (el anterior se invalida).
    El token vence a las TOKEN_TTL_HOURS horas.
    """

    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "panel_login"

    @extend_schema(request=LoginSerializer, responses=OpenApiTypes.OBJECT)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if user is None or not user.is_active or not user.is_staff:
            return Response(
                {"detail": "Usuario o contraseña incorrectos."}, status=status.HTTP_400_BAD_REQUEST
            )
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)
        update_last_login(None, user)
        return Response({"token": token.key, "user": user_payload(user)})


class LogoutView(APIView):
    """Invalida el token de la sesión actual."""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=None, responses={204: None})
    def post(self, request):
        if isinstance(request.auth, Token):
            request.auth.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    """Datos del usuario de la sesión actual."""

    permission_classes = [permissions.IsAdminUser]

    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request):
        return Response(user_payload(request.user))


class StaffUsersView(APIView):
    """Administradores del sitio (usuarios del staff), para la sección 'Gestionar usuarios'."""

    permission_classes = [permissions.IsAdminUser]

    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request):
        users = get_user_model().objects.filter(is_staff=True).order_by("-is_superuser", "username")
        return Response(
            [
                {
                    **user_payload(user),
                    "id": user.pk,
                    "is_active": user.is_active,
                    "last_login": user.last_login,
                    "date_joined": user.date_joined,
                }
                for user in users
            ]
        )
