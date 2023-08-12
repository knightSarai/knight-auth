from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from knightauth.auth import TokenAuthentication
from knightauth.api import auth_router

api = NinjaAPI(auth=TokenAuthentication())
api.add_router('auth/', auth_router)


@api.get('/test')
def test(request):
    return {'message': 'Hello, world!', 'user': request.user.username}


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]
