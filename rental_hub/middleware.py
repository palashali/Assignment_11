class RoleContextMiddleware:
    """
    Middleware that adds user role information and dashboard counts
    to the request object for easy access across views and templates.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            request.is_owner = getattr(request.user, 'is_owner', False)
            request.is_tenant = getattr(request.user, 'is_tenant', False)
            request.user_role = getattr(request.user, 'role', 'TENANT')
        else:
            request.is_owner = False
            request.is_tenant = False
            request.user_role = None

        response = self.get_response(request)
        return response


class SecurityHeadersMiddleware:
    """
    Middleware to ensure proper security response headers.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        return response
