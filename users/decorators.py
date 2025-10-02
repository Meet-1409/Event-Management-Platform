"""
Security decorators for views and functions
"""
import functools
import time
from django.core.cache import cache
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


def rate_limit(max_requests=60, window_seconds=60, key_func=None):
    """
    Rate limiting decorator
    
    Args:
        max_requests: Maximum number of requests allowed
        window_seconds: Time window in seconds
        key_func: Function to generate cache key (defaults to IP-based)
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(request)
            else:
                # Default: use IP address
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = x_forwarded_for.split(',')[0]
                else:
                    ip = request.META.get('REMOTE_ADDR')
                cache_key = f"rate_limit_{ip}_{view_func.__name__}"
            
            # Check rate limit
            current_time = time.time()
            requests = cache.get(cache_key, [])
            
            # Remove old requests
            requests = [req_time for req_time in requests if current_time - req_time < window_seconds]
            
            # Check if limit exceeded
            if len(requests) >= max_requests:
                logger.warning(f"Rate limit exceeded for {cache_key}")
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'retry_after': window_seconds
                }, status=429)
            
            # Add current request
            requests.append(current_time)
            cache.set(cache_key, requests, window_seconds)
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def require_https(view_func):
    """
    Require HTTPS for the view
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.is_secure():
            return JsonResponse({'error': 'HTTPS required'}, status=400)
        return view_func(request, *args, **kwargs)
    
    return wrapper


def require_user_agent(view_func):
    """
    Require User-Agent header (basic bot protection)
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        if not user_agent:
            return JsonResponse({'error': 'User-Agent required'}, status=400)
        
        # Block suspicious user agents
        suspicious_agents = ['curl', 'wget', 'python-requests', 'bot', 'crawler', 'spider']
        if any(agent in user_agent.lower() for agent in suspicious_agents):
            logger.warning(f"Suspicious User-Agent blocked: {user_agent}")
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def require_referer(view_func):
    """
    Require Referer header (basic CSRF protection)
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            referer = request.META.get('HTTP_REFERER', '')
            host = request.get_host()
            
            if not referer or not referer.startswith(f'http://{host}') and not referer.startswith(f'https://{host}'):
                logger.warning(f"Missing or invalid Referer header: {referer}")
                return JsonResponse({'error': 'Invalid request'}, status=400)
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def check_permissions(*permissions):
    """
    Check user permissions
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'Authentication required'}, status=401)
            
            for permission in permissions:
                if not request.user.has_perm(permission):
                    logger.warning(f"Permission denied for user {request.user.username}: {permission}")
                    return JsonResponse({'error': 'Permission denied'}, status=403)
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def check_user_role(*roles):
    """
    Check user role
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'Authentication required'}, status=401)
            
            user_role = getattr(request.user, 'role', None)
            if user_role not in roles:
                logger.warning(f"Role access denied for user {request.user.username}: {user_role}")
                return JsonResponse({'error': 'Access denied'}, status=403)
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def log_activity(activity_type):
    """
    Log user activity
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                logger.info(f"User {request.user.username} performed {activity_type}")
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def secure_view(view_func):
    """
    Apply multiple security measures to a view
    """
    @functools.wraps(view_func)
    @csrf_protect
    @never_cache
    @require_user_agent
    @rate_limit(max_requests=100, window_seconds=60)
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    
    return wrapper


def admin_required(view_func):
    """
    Require admin access
    """
    @functools.wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied("Admin access required")
        return view_func(request, *args, **kwargs)
    
    return wrapper


def manager_required(view_func):
    """
    Require manager access
    """
    @functools.wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not (request.user.is_staff or getattr(request.user, 'role', None) == 'manager'):
            raise PermissionDenied("Manager access required")
        return view_func(request, *args, **kwargs)
    
    return wrapper


def api_view_security(view_func):
    """
    Security decorator for API views
    """
    @functools.wraps(view_func)
    @csrf_protect
    @require_http_methods(['GET', 'POST', 'PUT', 'DELETE'])
    @rate_limit(max_requests=200, window_seconds=60)
    @require_user_agent
    def wrapper(request, *args, **kwargs):
        # Add security headers
        response = view_func(request, *args, **kwargs)
        if hasattr(response, 'headers'):
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    
    return wrapper


# Class-based view decorators
def method_rate_limit(max_requests=60, window_seconds=60):
    """
    Rate limiting for class-based views
    """
    def decorator(cls):
        for method_name in ['get', 'post', 'put', 'delete', 'patch']:
            if hasattr(cls, method_name):
                method = getattr(cls, method_name)
                decorated_method = rate_limit(max_requests, window_seconds)(method)
                setattr(cls, method_name, decorated_method)
        return cls
    return decorator


def method_secure_view(cls):
    """
    Apply security to class-based view methods
    """
    for method_name in ['get', 'post', 'put', 'delete', 'patch']:
        if hasattr(cls, method_name):
            method = getattr(cls, method_name)
            decorated_method = secure_view(method)
            setattr(cls, method_name, decorated_method)
    return cls
