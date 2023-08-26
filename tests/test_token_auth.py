from datetime import timedelta

import pytest
from django.test import RequestFactory
from django.urls import reverse_lazy

from knightauth.auth import TokenAuthentication
from knightauth.models import AuthToken
from knightauth.signals import token_expired


@pytest.fixture
def setup_user(django_user_model):
    django_user_model.objects.create_user(username='john.doe', email='john.doe@example.com', password='qwerty1200')
    django_user_model.objects.create_user(username='jane.doe', email='jane.doe@example.com', password='qwerty1200')


@pytest.mark.django_db
def test_initial_auth_token_to_be_zero(setup_user):
    assert AuthToken.objects.count() == 0


@pytest.mark.django_db
def test_login_creates_auth_token(setup_user, django_user_model, client):
    request_kwargs = {
        'path': reverse_lazy('api-1.0.0:token_login'),
        'data': {
            django_user_model.USERNAME_FIELD: "john.doe",
            "password": "qwerty1200"
        },
        'content_type': 'application/json'
    }

    client.post(**request_kwargs)
    client.post(**request_kwargs)
    client.post(**request_kwargs)

    assert AuthToken.objects.count() == 3
    assert all(obj.token_key for obj in AuthToken.objects.all())


@pytest.mark.django_db
def test_login_returns_serialized_token(setup_user, django_user_model, client):
    request_kwargs = {
        'path': reverse_lazy('api-1.0.0:token_login'),
        'data': {
            django_user_model.USERNAME_FIELD: "john.doe",
            "password": "qwerty1200"
        },
        'content_type': 'application/json'
    }

    response = client.post(**request_kwargs)
    json_response = response.json()

    assert response.status_code == 200
    assert json_response.get('token')


@pytest.mark.django_db
def test_logout_deletes_keys(setup_user, django_user_model, client):
    request_kwargs = {
        'path': reverse_lazy('api-1.0.0:token_login'),
        'data': {
            django_user_model.USERNAME_FIELD: "john.doe",
            "password": "qwerty1200"
        },
        'content_type': 'application/json'
    }

    client.post(**request_kwargs)
    response = client.post(**request_kwargs).json()

    request_kwargs = {
        'path': reverse_lazy('api-1.0.0:token_logout'),
        'content_type': 'application/json',
        'HTTP_AUTHORIZATION': response.get('token')
    }

    client.post(**request_kwargs)

    assert AuthToken.objects.count() == 1


@pytest.mark.django_db
def test_logout_all_deletes_keys(setup_user, django_user_model, client):
    request_kwargs = {
        'path': reverse_lazy('api-1.0.0:token_login'),
        'data': {
            django_user_model.USERNAME_FIELD: "john.doe",
            "password": "qwerty1200"
        },
        'content_type': 'application/json'
    }

    client.post(**request_kwargs)
    response = client.post(**request_kwargs).json()

    request_kwargs = {
        'path': reverse_lazy('api-1.0.0:token_logoutall'),
        'content_type': 'application/json',
        'HTTP_AUTHORIZATION': response.get('token'),
    }

    client.post(**request_kwargs)

    assert AuthToken.objects.count() == 0


@pytest.mark.django_db
def test_logout_all_deletes_keys_for_user(setup_user, django_user_model, client):
    request_kwargs = {
        'path': reverse_lazy('api-1.0.0:token_login'),
        'data': {
            django_user_model.USERNAME_FIELD: "john.doe",
            "password": "qwerty1200"
        },
        'content_type': 'application/json'
    }
    client.post(**request_kwargs)

    request_kwargs['data'][django_user_model.USERNAME_FIELD] = "jane.doe"
    client.post(**request_kwargs)
    response = client.post(**request_kwargs).json()

    request_kwargs = {
        'path': reverse_lazy('api-1.0.0:token_logoutall'),
        'content_type': 'application/json',
        'HTTP_AUTHORIZATION': response.get('token'),
    }

    client.post(**request_kwargs)

    assert AuthToken.objects.count() == 1


@pytest.mark.django_db
def test_expired_tokens_login_fails(setup_user, django_user_model, client):
    _, token = AuthToken.objects.create(user=django_user_model.objects.first(), expiry=timedelta(seconds=0))

    request_kwargs = {
        'path': reverse_lazy('api-1.0.0:test'),
        'content_type': 'application/json',
        'HTTP_AUTHORIZATION': token
    }

    response = client.get(**request_kwargs)

    assert response.status_code == 401
    assert response.json().get('detail') == 'Unauthorized'


@pytest.mark.django_db
def test_token_authentication_with_valid_token(setup_user, django_user_model):
    user = django_user_model.objects.first()
    _, token = AuthToken.objects.create(user=user)

    auth_user = TokenAuthentication().authenticate(RequestFactory().get('/'), token)

    assert auth_user == user


@pytest.mark.django_db
def test_token_authentication_with_invalid_token(setup_user):
    rf = RequestFactory()

    assert TokenAuthentication().authenticate(RequestFactory().get('/'), '') is None
    assert TokenAuthentication().authenticate(RequestFactory().get('/'), 'This is token') is None


@pytest.mark.django_db
def test_expiry_signals(setup_user, django_user_model, client):
    signal_fired = False

    def signal_handler(sender, **kwargs):
        nonlocal signal_fired
        signal_fired = True

    token_expired.connect(signal_handler)

    _, token = AuthToken.objects.create(user=django_user_model.objects.first(), expiry=timedelta(seconds=0))

    request_kwargs = {
        'path': reverse_lazy('api-1.0.0:test'),
        'content_type': 'application/json',
        'HTTP_AUTHORIZATION': token
    }

    client.get(**request_kwargs)

    assert signal_fired
