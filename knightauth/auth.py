import binascii
from hmac import compare_digest

from django.utils import timezone
from ninja.security import APIKeyHeader

from knightauth.crypto import hash_token
from knightauth.models import get_token_model
from knightauth.settings import CONSTANTS, knight_auth_settings
from knightauth.signals import token_expired


class TokenAuthentication(APIKeyHeader):
    param_name = "Authorization"

    def authenticate(self, request, token):
        user, auth_token = self.authenticate_credentials(token)
        request._auth = auth_token

        return user

    def authenticate_credentials(self, token):
        if not token:
            return None, None

        auth_tokens = (
            get_token_model()
            .objects
            .filter(token_key=token[:CONSTANTS.TOKEN_KEY_LENGTH])
        )

        for auth_token in auth_tokens:
            if self._cleanup_token(auth_token):
                continue

            try:
                digest = hash_token(token)
            except (TypeError, binascii.Error):
                return None, None

            if compare_digest(digest, auth_token.digest):
                if knight_auth_settings.AUTO_REFRESH and auth_token.expiry:
                    self.renew_token(auth_token)

                return self.validate_user(auth_token)

        return None, None

    def renew_token(self, auth_token):
        current_expiry = auth_token.expiry
        new_expiry = timezone.now() + knight_auth_settings.TOKEN_TTL
        auth_token.expiry = new_expiry
        # Throttle refreshing of token to avoid db writes
        delta = (new_expiry - current_expiry).total_seconds()
        if delta > knight_auth_settings.MIN_REFRESH_INTERVAL:
            auth_token.save(update_fields=('expiry',))

    def validate_user(self, auth_token):
        if not auth_token.user.is_active:
            return None, None

        return auth_token.user, auth_token

    def _cleanup_token(self, auth_token):
        for other_token in auth_token.user.auth_token_set.all():
            if other_token.digest != auth_token.digest and other_token.expiry:
                if other_token.expiry < timezone.now():
                    other_token.delete()
                    username = other_token.user.get_username()
                    token_expired.send(
                        sender=self.__class__,
                        username=username,
                        source="other_token"
                    )

        if auth_token.expiry is not None:
            if auth_token.expiry < timezone.now():
                username = auth_token.user.get_username()
                auth_token.delete()
                token_expired.send(
                    sender=self.__class__,
                    username=username,
                    source="auth_token"
                )
                return True

        return False


