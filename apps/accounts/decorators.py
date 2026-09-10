from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .permissions import has_perm

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


def permission_required(perm_code):
    """Decorator checking specific functional permission code."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(f"/accounts/login/?next={request.path}")
            if has_perm(request.user, perm_code):
                return view_func(request, *args, **kwargs)
            messages.error(request, "Access Denied: You lack authorization for this operation.")
            return redirect('dashboard')
        return _wrapped_view
    return decorator


def admin_required(view_func):
    return role_required(['ADMIN'])(view_func)


def secretary_required(view_func):
    return role_required(['ADMIN', 'SECRETARY'])(view_func)


def treasurer_required(view_func):
    return role_required(['ADMIN', 'TREASURER', 'ACCOUNTANT'])(view_func)


def financial_required(view_func):
    return role_required(['ADMIN', 'TREASURER', 'ACCOUNTANT'])(view_func)


def committee_required(view_func):
    return role_required(['ADMIN', 'SECRETARY', 'TREASURER', 'ACCOUNTANT', 'COMMITTEE', 'FACILITY_MGR'])(view_func)


def facility_required(view_func):
    return role_required(['ADMIN', 'FACILITY_MGR', 'SECRETARY'])(view_func)


def guard_required(view_func):
    return role_required(['ADMIN', 'GUARD'])(view_func)


def staff_required(view_func):
    return role_required(['ADMIN', 'STAFF', 'FACILITY_MGR'])(view_func)


def resident_required(view_func):
    return role_required(['ADMIN', 'SECRETARY', 'TREASURER', 'COMMITTEE', 'OWNER', 'TENANT', 'RESIDENT'])(view_func)

