from functools import wraps
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, get_object_or_404
from properties.models import Property


def owner_required(view_func):
    """
    Decorator for views that checks that the user is logged in and is a Property Owner.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in as a Property Owner to access this page.")
            return redirect('accounts:login')
        if not request.user.is_owner:
            messages.error(request, "Access restricted. You must be a Property Owner to perform this action.")
            return redirect('properties:property_list')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def tenant_required(view_func):
    """
    Decorator for views that checks that the user is logged in and is a Tenant.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to perform this action.")
            return redirect('accounts:login')
        if not request.user.is_tenant:
            messages.error(request, "Access restricted. Only tenants can perform this action.")
            return redirect('properties:property_list')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def property_owner_required(view_func):
    """
    Decorator to ensure the logged-in user is the actual owner of the property specified by 'pk' in URL kwargs.
    Prevents unauthorized property modification or deletion.
    """
    @wraps(view_func)
    def _wrapped_view(request, pk=None, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to manage your property.")
            return redirect('accounts:login')

        property_obj = get_object_or_404(Property, pk=pk)
        if property_obj.owner != request.user and not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to manage this property.")
        return view_func(request, pk=pk, *args, **kwargs)
    return _wrapped_view
