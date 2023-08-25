from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

# from knightauth.api import cookie_auth_router
from knightauth.api import token_auth_router, register_router
from knightauth.auth import TokenAuthentication

# from ninja.security import SessionAuth

token_based_api = NinjaAPI(auth=TokenAuthentication(), version='1.0.0', urls_namespace='token')
token_based_api.add_router('auth/', token_auth_router)
token_based_api.add_router('auth/', register_router)

# session_based_api = NinjaAPI(auth=SessionAuth(), csrf=True, version='1.0.0', urls_namespace='session')
# session_based_api.add_router('auth/', cookie_auth_router)
# session_based_api.add_router('auth/', register_router)


@token_based_api.get('/test-token-auth')
def token_test(request):
    return {'message': 'Hello, world!', 'user': request.auth.username}


# @session_based_api.get('/test-session-auth')
# def session_test(request):
#     return {'message': 'Hello, world!', 'user': request.auth.username}


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', token_based_api.urls),
    # path('api/v1/s/', session_based_api.urls),
]
