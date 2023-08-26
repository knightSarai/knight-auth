from django.contrib.auth import authenticate, login as django_login, logout as django_logout, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.validators import EmailValidator
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import ensure_csrf_cookie
from ninja import Router
from ninja.responses import Response

from knightauth.models import get_token_model
from knightauth.schemas import LoginIn, ErrorOut, LoginSuccessOut, UserRegisterSchema
from knightauth.settings import knight_auth_settings

token_auth_router = Router()


@token_auth_router.post(
    "login",
    auth=None,
    response={200: LoginSuccessOut, frozenset({401, 403}): ErrorOut},
    url_name="token_login"
)
def token_login(request, payload: LoginIn):
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


@token_auth_router.post("logout", response={204: None, 400: ErrorOut}, url_name="token_logout")
def token_logout(request):
    if not hasattr(request, "_auth") or not request._auth:
        return 400, {
            "message": ""
                       "Attempting to log out using an authentication method different from the one used for login."
                       "Consider using session authentication instead"
                       ""
        }

    request._auth.delete()
    user_logged_out.send(sender=request.user.__class__, request=request, user=request.user)

    return 204, None


@token_auth_router.post("logoutall", response={204: None, 400: ErrorOut}, url_name="token_logoutall")
def token_logout_all(request):
    if not request.auth.auth_token_set.exists():
        return 400, {
            "message": ""
                       "Attempting to log out using an authentication method different from the one used for login."
                       "Consider using session authentication instead"
                       ""
        }

    request.auth.auth_token_set.all().delete()
    user_logged_out.send(sender=request.user.__class__, request=request, user=request.user)
    return 204, None


session_auth_router = Router()


@session_auth_router.post("login", auth=None, response={200: None, 400: ErrorOut}, url_name="session_login")
def session_login(request, payload: LoginIn):
    username = payload.username
    password = payload.password

    if username is None or password is None:
        return 400, {"message": "Please provide username and password."}

    user = authenticate(username=username, password=password)

    if user is None:
        return 400, {"message": "Invalid credentials."}

    django_login(request, user)

    return 200, None


@session_auth_router.post("logout", response={200: None}, url_name="session_logout")
def session_logout(request):
    django_logout(request)

    return 200, None


@session_auth_router.get("verify-session", auth=None, url_name="verify_session")
@ensure_csrf_cookie
def verify_session(request):
    if not request.user.is_authenticated:
        return Response({"ok": None}, status=200)
    return Response({"ok": request.user.username}, status=200)


register_router = Router()


@register_router.post("register", auth=None, response={201: None, 400: ErrorOut}, url_name="register_user")
def register(request, user_payload: UserRegisterSchema):
    try:
        validate_password(user_payload.password)
    except ValidationError as e:
        return 400, {"message": e.messages}

    if user_payload.password != user_payload.password_confirm:
        return 400, {"message": "Password does not match"}

    email_validator = EmailValidator()
    try:
        email_validator(user_payload.email)
    except ValidationError as e:
        return 400, {"message": e.messages}

    User = get_user_model()

    email_exist = User.objects.filter(email=user_payload.email).exists()
    if email_exist:
        return 400, {"message": "Email already exist"}

    username_exist = User.objects.filter(username=user_payload.username).exists()
    if username_exist:
        return 400, {"message": "Username already exist"}

    User.objects.create_user(
        username=user_payload.username,
        email=user_payload.email,
        password=user_payload.password
    )

    return 201, None
