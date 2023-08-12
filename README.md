# knight-auth
Knight Auth is a versatile authentication package designed exclusively for Django Ninja. Inspired by the popular Django Rest Knox project, Knight Auth brings the power of token-based authentication to your Django Ninja APIs. With an emphasis on flexibility, security, and seamless integration, Knight Auth simplifies user authentication, allowing you to focus on building exceptional API experiences.

# Setup
## Installation
```bash
pip install django django-ninja
pip install knight-auth
```

## Usage
### 1. Add Knight Auth to your Django project
```python
INSTALLED_APPS = [
    ...
    'knight_auth',
    ...
]
```

### 2. Add Knight Auth to your Ninja router
```python
from ninja import NinjaAPI
from knightauth.auth import TokenAuthentication
from knightauth.api import auth_router


api = NinjaAPI(auth=TokenAuthentication())
api.add_router('auth/', auth_router)

urlpatterns = [
    ....
    path('api/', api.urls),
]
```

### 4. An example of an endpoint that requires authentication
```python

@api.get('/test')
def test(request):
    return {'message': 'Hello, world!', 'user': request.auth.username}
```

### 5. That's it! You're done!



