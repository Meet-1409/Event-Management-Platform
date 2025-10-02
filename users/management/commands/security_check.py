"""
Django management command for security checks
Usage: python manage.py security_check
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from django.test import Client
from django.contrib.auth import get_user_model
import os
import sys

User = get_user_model()


class Command(BaseCommand):
    help = 'Perform comprehensive security checks on the Event Manager platform'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Attempt to fix common security issues',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )
    
    def handle(self, *args, **options):
        self.verbose = options['verbose']
        self.fix = options['fix']
        
        self.stdout.write(
            self.style.SUCCESS('🔒 Event Manager Security Check')
        )
        self.stdout.write('=' * 50)
        
        # Run security checks
        self.check_django_settings()
        self.check_security_headers()
        self.check_file_permissions()
        self.check_database_security()
        self.check_secret_key()
        self.check_debug_mode()
        self.check_allowed_hosts()
        self.check_ssl_settings()
        self.check_session_security()
        self.check_csrf_settings()
        
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write('✅ Security check completed!')
    
    def check_django_settings(self):
        """Check Django security settings"""
        self.stdout.write('\n🔧 Checking Django Security Settings...')
        
        # Check SECRET_KEY
        if settings.SECRET_KEY:
            if 'django-insecure' in settings.SECRET_KEY:
                self.stdout.write(
                    self.style.WARNING('⚠️  SECRET_KEY contains default value')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('✅ SECRET_KEY is properly configured')
                )
        else:
            self.stdout.write(
                self.style.ERROR('❌ SECRET_KEY is not set')
            )
    
    def check_security_headers(self):
        """Check security headers configuration"""
        self.stdout.write('\n🛡️ Checking Security Headers...')
        
        security_settings = [
            ('SECURE_BROWSER_XSS_FILTER', True),
            ('SECURE_CONTENT_TYPE_NOSNIFF', True),
            ('X_FRAME_OPTIONS', 'DENY'),
            ('SECURE_HSTS_SECONDS', 31536000),
        ]
        
        for setting, expected_value in security_settings:
            actual_value = getattr(settings, setting, None)
            if actual_value == expected_value:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {setting}: {actual_value}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  {setting}: {actual_value} (expected: {expected_value})')
                )
    
    def check_file_permissions(self):
        """Check file permissions"""
        self.stdout.write('\n📁 Checking File Permissions...')
        
        # Check media directory
        media_dir = settings.MEDIA_ROOT
        if os.path.exists(media_dir):
            stat_info = os.stat(media_dir)
            permissions = oct(stat_info.st_mode)[-3:]
            if permissions == '755':
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Media directory permissions: {permissions}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Media directory permissions: {permissions} (recommended: 755)')
                )
        
        # Check static files
        static_dir = settings.STATIC_ROOT
        if os.path.exists(static_dir):
            stat_info = os.stat(static_dir)
            permissions = oct(stat_info.st_mode)[-3:]
            if permissions == '755':
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Static directory permissions: {permissions}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Static directory permissions: {permissions} (recommended: 755)')
                )
    
    def check_database_security(self):
        """Check database security"""
        self.stdout.write('\n🗄️ Checking Database Security...')
        
        db_config = settings.DATABASES['default']
        
        # Check if using SQLite in production
        if db_config['ENGINE'] == 'django.db.backends.sqlite3':
            if not settings.DEBUG:
                self.stdout.write(
                    self.style.WARNING('⚠️  SQLite database in production (not recommended)')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('✅ SQLite database for development')
                )
        
        # Check database permissions
        if 'OPTIONS' in db_config:
            options = db_config['OPTIONS']
            if 'init_command' in options:
                self.stdout.write(
                    self.style.SUCCESS('✅ Database init command configured')
                )
    
    def check_secret_key(self):
        """Check SECRET_KEY security"""
        self.stdout.write('\n🔑 Checking SECRET_KEY Security...')
        
        secret_key = settings.SECRET_KEY
        
        if not secret_key:
            self.stdout.write(
                self.style.ERROR('❌ SECRET_KEY is not set')
            )
            return
        
        # Check length
        if len(secret_key) < 50:
            self.stdout.write(
                self.style.WARNING('⚠️  SECRET_KEY is too short (recommended: 50+ characters)')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ SECRET_KEY length is adequate')
            )
        
        # Check for common patterns
        common_patterns = ['django-insecure', 'your-secret-key', 'change-this']
        for pattern in common_patterns:
            if pattern in secret_key.lower():
                self.stdout.write(
                    self.style.WARNING(f'⚠️  SECRET_KEY contains common pattern: {pattern}')
                )
                break
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ SECRET_KEY does not contain common patterns')
            )
    
    def check_debug_mode(self):
        """Check DEBUG mode"""
        self.stdout.write('\n🐛 Checking DEBUG Mode...')
        
        if settings.DEBUG:
            self.stdout.write(
                self.style.WARNING('⚠️  DEBUG mode is enabled (disable in production)')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ DEBUG mode is disabled')
            )
    
    def check_allowed_hosts(self):
        """Check ALLOWED_HOSTS configuration"""
        self.stdout.write('\n🌐 Checking ALLOWED_HOSTS...')
        
        allowed_hosts = settings.ALLOWED_HOSTS
        
        if not allowed_hosts:
            self.stdout.write(
                self.style.ERROR('❌ ALLOWED_HOSTS is not configured')
            )
        elif '*' in allowed_hosts:
            self.stdout.write(
                self.style.WARNING('⚠️  ALLOWED_HOSTS contains wildcard (*)')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'✅ ALLOWED_HOSTS configured: {allowed_hosts}')
            )
    
    def check_ssl_settings(self):
        """Check SSL/TLS settings"""
        self.stdout.write('\n🔒 Checking SSL/TLS Settings...')
        
        ssl_settings = [
            ('SECURE_SSL_REDIRECT', False),
            ('SESSION_COOKIE_SECURE', False),
            ('CSRF_COOKIE_SECURE', False),
        ]
        
        for setting, default_value in ssl_settings:
            actual_value = getattr(settings, setting, default_value)
            if actual_value:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {setting}: {actual_value}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  {setting}: {actual_value} (recommended: True for production)')
                )
    
    def check_session_security(self):
        """Check session security settings"""
        self.stdout.write('\n🍪 Checking Session Security...')
        
        session_settings = [
            ('SESSION_COOKIE_HTTPONLY', True),
            ('SESSION_COOKIE_SECURE', False),
            ('SESSION_COOKIE_SAMESITE', 'Lax'),
            ('SESSION_EXPIRE_AT_BROWSER_CLOSE', True),
        ]
        
        for setting, expected_value in session_settings:
            actual_value = getattr(settings, setting, None)
            if actual_value == expected_value:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {setting}: {actual_value}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  {setting}: {actual_value} (expected: {expected_value})')
                )
    
    def check_csrf_settings(self):
        """Check CSRF settings"""
        self.stdout.write('\n🛡️ Checking CSRF Settings...')
        
        csrf_settings = [
            ('CSRF_COOKIE_SECURE', False),
            ('CSRF_COOKIE_HTTPONLY', True),
            ('CSRF_COOKIE_SAMESITE', 'Lax'),
            ('CSRF_USE_SESSIONS', True),
        ]
        
        for setting, expected_value in csrf_settings:
            actual_value = getattr(settings, setting, None)
            if actual_value == expected_value:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {setting}: {actual_value}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  {setting}: {actual_value} (expected: {expected_value})')
                )
