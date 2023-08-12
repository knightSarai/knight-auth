from django.contrib.auth import authenticate
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.utils import timezone
from ninja import Router
from ninja.responses import codes_4xx, codes_2xx

from knightauth.models import get_token_model
from knightauth.schemas import LoginIn, LoginErrorOut, LoginSuccessOut
from knightauth.settings import knight_auth_settings

auth_router = Router()


@auth_router.post("/login", auth=None, response={codes_2xx: LoginSuccessOut, codes_4xx: LoginErrorOut})
def login(request, payload: LoginIn):
    if knight_auth_settings.TOKEN_LIMIT_PER_USER is not None:
        now = timezone.now()
        token_count = (
            request
            .user
            .auth_token_set
            .filter(created__gte=now)
            .count()
        )

        if token_count >= knight_auth_settings.TOKEN_LIMIT_PER_USER:
            return 403, {"message": "Maximum amount of tokens allowed per user exceeded."}

    user = authenticate(request, **payload.dict())

    if user is None:
        return 401, {"message": "Invalid credentials"}

    instance, token = (
        get_token_model()
        .objects
        .create(
            user=user,
            prefix=knight_auth_settings.TOKEN_PREFIX,
            expiry=knight_auth_settings.TOKEN_TTL
        )
    )

    user_logged_in.send(sender=user.__class__, request=request, user=user)

    return 200, {
        "token": token,
        "expiry": instance.expiry
    }


@auth_router.post("/logout", response={codes_2xx: None})
def logout(request):
    request._auth.delete()
    user_logged_out.send(sender=request.user.__class__, request=request, user=request.user)

    return 204, None


@auth_router.post("/logoutall", response={codes_2xx: None})
def logout(request):
    request.user.auth_token_set.all().delete()
    user_logged_out.send(sender=request.user.__class__, request=request, user=request.user)
    return 204, None
