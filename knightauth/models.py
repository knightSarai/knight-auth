from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils import timezone

from knightauth import crypto
from knightauth.settings import CONSTANTS, knight_auth_settings

sha = knight_auth_settings.SECURE_HASH_ALGORITHM

User = get_user_model()


class AuthTokenManager(models.Manager):
    def create(
            self,
            user,
            expiry=knight_auth_settings.TOKEN_TTL,
            prefix=knight_auth_settings.TOKEN_PREFIX
    ):
        token = prefix + crypto.create_token_string()
        digest = crypto.hash_token(token)
        if expiry is not None:
            expiry = timezone.now() + expiry
        instance = super(AuthTokenManager, self).create(
            token_key=token[:CONSTANTS.TOKEN_KEY_LENGTH], digest=digest,
            user=user, expiry=expiry)
        return instance, token


class AbstractAuthToken(models.Model):
    objects = AuthTokenManager()

    digest = models.CharField(
        max_length=CONSTANTS.DIGEST_LENGTH,
        primary_key=True
    )
    token_key = models.CharField(
        max_length=CONSTANTS.MAXIMUM_TOKEN_PREFIX_LENGTH + CONSTANTS.TOKEN_KEY_LENGTH,
        db_index=True
    )
    user = models.ForeignKey(
        User,
        null=False,
        blank=False,
        related_name='auth_token_set',
        on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True)
    expiry = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return '%s : %s' % (self.digest, self.user)


class AuthToken(AbstractAuthToken):
    class Meta:
        swappable = 'KNIGHT_AUTH_TOKEN_MODEL'


def get_token_model():
    try:
        return apps.get_model(knight_auth_settings.TOKEN_MODEL, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured(
            "TOKEN_MODEL must be of the form 'app_label.model_name'"
        )
    except LookupError:
        raise ImproperlyConfigured(
            "TOKEN_MODEL refers to model '%s' that has not been installed"
            % knight_auth_settings.TOKEN_MODEL
        )
