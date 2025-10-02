"""
Custom security middleware for enhanced protection
"""
import time
from django.core.cache import cache
from django.http import HttpResponseForbidden, JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add additional security headers to all responses
    """
    
    def process_response(self, request, response):
        # Content Security Policy
        if hasattr(settings, 'CSP_DEFAULT_SRC'):
            csp_parts = []
            if hasattr(settings, 'CSP_DEFAULT_SRC'):
                csp_parts.append(f"default-src {' '.join(settings.CSP_DEFAULT_SRC)}")
            if hasattr(settings, 'CSP_SCRIPT_SRC'):
                csp_parts.append(f"script-src {' '.join(settings.CSP_SCRIPT_SRC)}")
            if hasattr(settings, 'CSP_STYLE_SRC'):
                csp_parts.append(f"style-src {' '.join(settings.CSP_STYLE_SRC)}")
            if hasattr(settings, 'CSP_FONT_SRC'):
                csp_parts.append(f"font-src {' '.join(settings.CSP_FONT_SRC)}")
            if hasattr(settings, 'CSP_IMG_SRC'):
                csp_parts.append(f"img-src {' '.join(settings.CSP_IMG_SRC)}")
            if hasattr(settings, 'CSP_CONNECT_SRC'):
                csp_parts.append(f"connect-src {' '.join(settings.CSP_CONNECT_SRC)}")
            if hasattr(settings, 'CSP_FRAME_SRC'):
                csp_parts.append(f"frame-src {' '.join(settings.CSP_FRAME_SRC)}")
            
            if csp_parts:
                response['Content-Security-Policy'] = '; '.join(csp_parts)
        
        # Additional security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = getattr(settings, 'SECURE_REFERRER_POLICY', 'same-origin')
        response['Cross-Origin-Opener-Policy'] = getattr(settings, 'SECURE_CROSS_ORIGIN_OPENER_POLICY', 'same-origin')
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Rate limiting middleware to prevent abuse
    """
    
    def process_request(self, request):
        # Skip rate limiting for static files and admin
        if request.path.startswith('/static/') or request.path.startswith('/media/') or request.path.startswith('/admin/'):
            return None
        
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # Rate limiting rules
        rate_limit_key = f"rate_limit_{ip}"
        current_time = time.time()
        
        # Check if IP is rate limited
        requests = cache.get(rate_limit_key, [])
        
        # Remove requests older than 1 minute
        requests = [req_time for req_time in requests if current_time - req_time < 60]
        
        # Check if rate limit exceeded (100 requests per minute)
        if len(requests) >= 100:
            logger.warning(f"Rate limit exceeded for IP: {ip}")
            return HttpResponseForbidden("Rate limit exceeded. Please try again later.")
        
        # Add current request
        requests.append(current_time)
        cache.set(rate_limit_key, requests, 60)  # Cache for 1 minute
        
        return None


class LoginAttemptMiddleware(MiddlewareMixin):
    """
    Middleware to track and limit login attempts
    """
    
    def process_request(self, request):
        # Only process login requests
        if request.path not in ['/users/login/', '/accounts/login/'] or request.method != 'POST':
            return None
        
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # Check failed login attempts
        failed_attempts_key = f"failed_logins_{ip}"
        failed_attempts = cache.get(failed_attempts_key, 0)
        
        # Block if too many failed attempts (10 attempts per hour)
        if failed_attempts >= 10:
            logger.warning(f"Too many failed login attempts for IP: {ip}")
            return HttpResponseForbidden("Too many failed login attempts. Please try again later.")
        
        return None


@receiver(user_login_failed)
def track_failed_login(sender, credentials, request, **kwargs):
    """
    Track failed login attempts
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    failed_attempts_key = f"failed_logins_{ip}"
    failed_attempts = cache.get(failed_attempts_key, 0) + 1
    cache.set(failed_attempts_key, failed_attempts, 3600)  # Cache for 1 hour
    
    logger.warning(f"Failed login attempt from IP: {ip}, Attempts: {failed_attempts}")


@receiver(user_logged_in)
def reset_failed_logins(sender, request, user, **kwargs):
    """
    Reset failed login attempts on successful login
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    failed_attempts_key = f"failed_logins_{ip}"
    cache.delete(failed_attempts_key)
    
    logger.info(f"Successful login for user: {user.username} from IP: {ip}")
