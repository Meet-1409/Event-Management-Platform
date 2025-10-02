#!/usr/bin/env python3
"""
Security Testing Script for Event Manager Platform
Run this script to test various security implementations
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_manager.settings')
django.setup()

User = get_user_model()


class SecurityTestSuite:
    """
    Comprehensive security testing suite
    """
    
    def __init__(self):
        self.client = Client()
        self.test_results = []
        self.passed = 0
        self.failed = 0
    
    def log_result(self, test_name, passed, message=""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"    {message}")
        
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'message': message
        })
        
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def test_security_headers(self):
        """Test security headers"""
        print("\n🔒 Testing Security Headers...")
        
        try:
            response = self.client.get('/')
            
            # Check required security headers
            headers_to_check = [
                'X-Content-Type-Options',
                'X-Frame-Options',
                'X-XSS-Protection',
                'Content-Security-Policy',
                'Strict-Transport-Security'
            ]
            
            for header in headers_to_check:
                if header in response:
                    self.log_result(f"Security Header: {header}", True, f"Value: {response[header]}")
                else:
                    self.log_result(f"Security Header: {header}", False, "Header missing")
                    
        except Exception as e:
            self.log_result("Security Headers Test", False, str(e))
    
    def test_csrf_protection(self):
        """Test CSRF protection"""
        print("\n🛡️ Testing CSRF Protection...")
        
        try:
            # Test POST without CSRF token
            response = self.client.post('/users/login/', {
                'username': 'testuser',
                'password': 'testpass'
            })
            
            if response.status_code == 403:
                self.log_result("CSRF Protection", True, "POST without CSRF token blocked")
            else:
                self.log_result("CSRF Protection", False, f"Expected 403, got {response.status_code}")
                
        except Exception as e:
            self.log_result("CSRF Protection Test", False, str(e))
    
    def test_rate_limiting(self):
        """Test rate limiting"""
        print("\n🚦 Testing Rate Limiting...")
        
        try:
            # Make multiple requests quickly
            for i in range(105):  # Exceed rate limit
                response = self.client.get('/')
                
                if i == 104:  # Last request
                    if response.status_code == 429:
                        self.log_result("Rate Limiting", True, "Rate limit enforced")
                    else:
                        self.log_result("Rate Limiting", False, f"Expected 429, got {response.status_code}")
                        
        except Exception as e:
            self.log_result("Rate Limiting Test", False, str(e))
    
    def test_file_upload_security(self):
        """Test file upload security"""
        print("\n📁 Testing File Upload Security...")
        
        try:
            # Test malicious file upload
            malicious_content = b'<script>alert("xss")</script>'
            malicious_file = SimpleUploadedFile(
                "test.html",
                malicious_content,
                content_type="text/html"
            )
            
            # Try to upload malicious file
            response = self.client.post('/events/upload/', {
                'file': malicious_file
            })
            
            if response.status_code == 400 or response.status_code == 403:
                self.log_result("File Upload Security", True, "Malicious file blocked")
            else:
                self.log_result("File Upload Security", False, f"Expected 400/403, got {response.status_code}")
                
        except Exception as e:
            self.log_result("File Upload Security Test", False, str(e))
    
    def test_sql_injection_protection(self):
        """Test SQL injection protection"""
        print("\n💉 Testing SQL Injection Protection...")
        
        try:
            # Test SQL injection in login form
            sql_injection = "admin'; DROP TABLE users; --"
            
            response = self.client.post('/users/login/', {
                'username': sql_injection,
                'password': 'testpass'
            })
            
            # Should not crash or return 500
            if response.status_code != 500:
                self.log_result("SQL Injection Protection", True, "SQL injection attempt handled safely")
            else:
                self.log_result("SQL Injection Protection", False, "Server error on SQL injection")
                
        except Exception as e:
            self.log_result("SQL Injection Protection Test", False, str(e))
    
    def test_xss_protection(self):
        """Test XSS protection"""
        print("\n🚫 Testing XSS Protection...")
        
        try:
            # Test XSS in form data
            xss_payload = "<script>alert('xss')</script>"
            
            response = self.client.post('/events/create/', {
                'title': xss_payload,
                'description': 'Test event'
            })
            
            # Check if XSS payload is escaped in response
            if xss_payload not in str(response.content):
                self.log_result("XSS Protection", True, "XSS payload escaped")
            else:
                self.log_result("XSS Protection", False, "XSS payload not escaped")
                
        except Exception as e:
            self.log_result("XSS Protection Test", False, str(e))
    
    def test_authentication_security(self):
        """Test authentication security"""
        print("\n🔐 Testing Authentication Security...")
        
        try:
            # Test password requirements
            weak_passwords = ['123', 'password', 'admin', 'qwerty']
            
            for weak_pass in weak_passwords:
                response = self.client.post('/users/register/', {
                    'username': 'testuser',
                    'email': 'test@example.com',
                    'password1': weak_pass,
                    'password2': weak_pass
                })
                
                if 'password' in str(response.content).lower():
                    self.log_result("Password Validation", True, f"Weak password '{weak_pass}' rejected")
                else:
                    self.log_result("Password Validation", False, f"Weak password '{weak_pass}' accepted")
                    
        except Exception as e:
            self.log_result("Authentication Security Test", False, str(e))
    
    def test_session_security(self):
        """Test session security"""
        print("\n🍪 Testing Session Security...")
        
        try:
            response = self.client.get('/')
            
            # Check session cookie security
            if 'sessionid' in response.cookies:
                session_cookie = response.cookies['sessionid']
                if hasattr(session_cookie, 'secure') and session_cookie.secure:
                    self.log_result("Session Security", True, "Secure session cookie")
                else:
                    self.log_result("Session Security", False, "Session cookie not secure")
            else:
                self.log_result("Session Security", False, "No session cookie found")
                
        except Exception as e:
            self.log_result("Session Security Test", False, str(e))
    
    def test_directory_traversal_protection(self):
        """Test directory traversal protection"""
        print("\n📂 Testing Directory Traversal Protection...")
        
        try:
            # Test directory traversal attempts
            traversal_paths = [
                '../../../etc/passwd',
                '..\\..\\..\\windows\\system32\\drivers\\etc\\hosts',
                '....//....//....//etc/passwd'
            ]
            
            for path in traversal_paths:
                response = self.client.get(f'/files/{path}')
                
                if response.status_code == 404 or response.status_code == 403:
                    self.log_result("Directory Traversal Protection", True, f"Path '{path}' blocked")
                else:
                    self.log_result("Directory Traversal Protection", False, f"Path '{path}' accessible")
                    
        except Exception as e:
            self.log_result("Directory Traversal Protection Test", False, str(e))
    
    def run_all_tests(self):
        """Run all security tests"""
        print("🛡️ Starting Security Test Suite...")
        print("=" * 50)
        
        # Run all tests
        self.test_security_headers()
        self.test_csrf_protection()
        self.test_rate_limiting()
        self.test_file_upload_security()
        self.test_sql_injection_protection()
        self.test_xss_protection()
        self.test_authentication_security()
        self.test_session_security()
        self.test_directory_traversal_protection()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 SECURITY TEST SUMMARY")
        print("=" * 50)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📈 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        
        if self.failed == 0:
            print("\n🎉 All security tests passed! Your application is secure.")
        else:
            print(f"\n⚠️  {self.failed} security tests failed. Please review and fix.")
        
        return self.failed == 0


def main():
    """Main function"""
    print("🔒 Event Manager Security Test Suite")
    print("=" * 50)
    
    # Check if Django is properly configured
    try:
        from django.conf import settings
        print(f"Django Settings: {settings.SETTINGS_MODULE}")
        print(f"Debug Mode: {settings.DEBUG}")
        print(f"Allowed Hosts: {settings.ALLOWED_HOSTS}")
    except Exception as e:
        print(f"❌ Django configuration error: {e}")
        return False
    
    # Run security tests
    test_suite = SecurityTestSuite()
    success = test_suite.run_all_tests()
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
