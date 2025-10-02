from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse

def role_required(allowed_roles):
    """
    Decorator to restrict access to users with allowed user_type(s).
    Redirects to the appropriate dashboard if not allowed.
    Usage: @role_required(['user']) or @role_required(['manager', 'admin'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect('users:login')
            if user.user_type in allowed_roles:
                return view_func(request, *args, **kwargs)
            # Redirect based on user_type
            if user.user_type == 'user':
                return redirect(reverse('users:dashboard'))
            elif user.user_type == 'manager':
                return redirect(reverse('users:manager_dashboard'))
            elif user.user_type == 'admin':
                return redirect(reverse('users:admin_dashboard'))
            else:
                return redirect('users:login')
        return _wrapped_view
    return decorator
