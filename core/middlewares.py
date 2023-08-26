from ninja.operation import PathView


class ExemptAPIKeyAuthFromCSRFMiddleware:
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
