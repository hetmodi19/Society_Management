from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

def role_required(allowed_roles):
    """
    Decorator for views that checks whether a user has one of the allowed roles.
    If unauthenticated, redirects to login with next parameter.
    If authenticated but unauthorized, shows error message and redirects to dashboard.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(f"/accounts/login/?next={request.path}")
            
            if request.user.is_superuser or request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            
            messages.error(request, "Access Denied: You do not have permission to access that section.")
            return redirect('dashboard')
        return _wrapped_view
    return decorator


def admin_required(view_func):
    return role_required(['ADMIN'])(view_func)


def committee_required(view_func):
    return role_required(['ADMIN', 'COMMITTEE'])(view_func)


def guard_required(view_func):
    return role_required(['ADMIN', 'GUARD'])(view_func)


def staff_required(view_func):
    return role_required(['ADMIN', 'STAFF'])(view_func)


def resident_required(view_func):
    return role_required(['ADMIN', 'COMMITTEE', 'RESIDENT'])(view_func)
