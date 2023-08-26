# knight-auth
Knight Auth is a versatile authentication package designed exclusively for Django Ninja.
Inspired by the popular Django Rest Knox project, Knight Auth brings the power of token-based authentication to your Django Ninja APIs.
With an emphasis on flexibility, security, and seamless integration, Knight Auth simplifies user authentication, allowing you to focus on building exceptional API experiences.

Knight Auth has the following features:
* Provides two methods of authentication: token authentication and session authentication. You can use either or both methods in your project.
* CSRF support for session authentication.
* Register endpoint for creating new users.

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
from knightauth.api import token_auth_router


api = NinjaAPI(auth=TokenAuthentication())
api.add_router('auth/', token_auth_router)

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

## Combine multiple authentication methods
You can add multiple authentication methods to your NinjaAPI instance. For example, you can add both token authentication and session authentication to your project.

```python
from ninja import NinjaAPI
from ninja.security import SessionAuth
from knightauth.api import token_auth_router, session_auth_router
from knightauth.auth import TokenAuthentication

api = NinjaAPI(
    title='KnightAuth',
    auth=[TokenAuthentication(), SessionAuth()],
    csrf=True,
)
api.add_router('auth/', token_auth_router)
api.add_router('auth/session/', session_auth_router)
```
*NOTE: You have to set csrf=True for session authentication to work.

**NOTE: As for now, you still need to manage CSRF if you want combine token authentication and session authentication.
Even though token authentication does not require CSRF, This issue should be fixed in Django Ninja 1.0**

A workaround for this issue is to add a custom middleware to your project. The middleware should check if the request is authenticated with token authentication.
If the request is authenticated with token authentication, the middleware should set the CSRF cookie. Otherwise, the middleware should not set the CSRF cookie.
```python
from ninja.operation import PathView
class ExemptAPIKeyAuthFromCSRFMiddleware:
    """
    https://github.com/vitalik/django-ninja/issues/283
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated:
            return

        klass = getattr(view_func, "__self__", None)
        if not klass:
            return

        if isinstance(klass, PathView):
            request._dont_enforce_csrf_checks = True
```

## Register endpoint
Knight Auth provides a register endpoint for creating new users. You can add the register endpoint to your project by adding the following code to your NinjaAPI instance.
```python
from ninja import NinjaAPI
from knightauth.api import register_router

api = NinjaAPI(title='KnightAuth')

api.add_router('auth/', register_router)
```
Register endpoint does username, email and password validations, And password confirmation. Also it creates a new user based on django user model.
You can supply your own user model, but the endpoint only is going to populate username, email and password fields.
Sometimes you may want to create other Models that are related to the user model upon registration. For example, you may want to create a profile model for each user.
In this case, you can use the register signal to create the profile model (or any other functionality) upon registration. The register signal is sent after the user is created.
