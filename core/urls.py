from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from ninja.security import SessionAuth

from knightauth.api import token_auth_router, register_router, session_auth_router
from knightauth.auth import TokenAuthentication

api = NinjaAPI(
    title='KnightAuth',
    auth=[TokenAuthentication(), SessionAuth()],
    csrf=True,
    version='1.0.0',
    urls_namespace='token'
)
api.add_router('auth/', token_auth_router)
api.add_router('auth/session/', session_auth_router)
api.add_router('auth/', register_router)


@api.get('/test', url_name='test')
def token_test(request):
    return {'message': 'Hello, world!', 'user': request.auth.username}


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', api.urls),
]
