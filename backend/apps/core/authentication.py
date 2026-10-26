from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication


def token_is_expired(token):
    return token.created < timezone.now() - timedelta(hours=settings.TOKEN_TTL_HOURS)


class ExpiringTokenAuthentication(TokenAuthentication):
    """Token de DRF que vence TOKEN_TTL_HOURS horas después de iniciar sesión."""

    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)
        if token_is_expired(token):
            token.delete()
            raise exceptions.AuthenticationFailed("La sesión expiró. Vuelva a ingresar.")
        return user, token
