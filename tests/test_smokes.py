"""
Comprehensive smoke tests for 360° Event Manager
Tests all major user-facing functions and workflows
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from users.models import CustomUser
from events.models import Event, EventType
from venues.models import Venue, VenueCategory
from payments.models import Payment, PaymentMethod
from decimal import Decimal
from datetime import date, time
import json

User = get_user_model()

class AuthenticationSmokeTests(TestCase):
    """Test authentication flows"""
    
    def setUp(self):
        self.client = Client()
        
    def test_user_registration(self):
        """Test user registration flow"""
        # Registration page loads
        response = self.client.get('/users/register/')
        self.assertEqual(response.status_code, 200)
        
        # User can register
        response = self.client.post('/users/register/', {
            'username': 'smoketest',
            'email': 'smoke@example.com',
            'first_name': 'Smoke',
            'last_name': 'Test',
            'phone_number': '+919876543210',
            'password1': 'testpass123',
            'password2': 'testpass123'
        })
        self.assertIn(response.status_code, [200, 302])  # Success or redirect
        
    def test_user_login_logout(self):
        """Test login/logout flow"""
        # Create test user
        user = CustomUser.objects.create_user(
            username='logintest',
            email='login@example.com',
            password='testpass123',
            first_name='Login',
            last_name='Test'
        )
        
        # Login page loads
        response = self.client.get('/users/login/')
        self.assertEqual(response.status_code, 200)
        
        # User can login
        response = self.client.post('/users/login/', {
            'username': 'login@example.com',
            'password': 'testpass123'
        })
        self.assertIn(response.status_code, [200, 302])
        
        # User can logout
        response = self.client.get('/users/logout/')
        self.assertIn(response.status_code, [200, 302])
        
    def test_password_reset_flow(self):
        """Test password reset flow"""
        # Create test user
        CustomUser.objects.create_user(
            username='resettest',
            email='reset@example.com',
            password='oldpass123'
        )
        
        # Forgot password page loads
        response = self.client.get('/users/forgot-password/')
        self.assertEqual(response.status_code, 200)
        
        # Can submit forgot password request
        response = self.client.post('/users/forgot-password/', {
            'email': 'reset@example.com'
        })
        self.assertIn(response.status_code, [200, 302])

class ProfileSmokeTests(TestCase):
    """Test profile management"""
    
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='profiletest',
            email='profile@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='profile@example.com', password='testpass123')
        
    def test_profile_view_and_edit(self):
        """Test profile viewing and editing"""
        # Profile page loads
        response = self.client.get('/users/profile/')
        self.assertEqual(response.status_code, 200)
        
        # Dashboard loads
        response = self.client.get('/users/dashboard/')
        self.assertEqual(response.status_code, 200)
        
        # Change password page loads
        response = self.client.get('/users/change-password/')
        self.assertEqual(response.status_code, 200)

class EventsSmokeTests(TestCase):
    """Test event browsing and management"""
    
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='eventtest',
            email='event@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='event@example.com', password='testpass123')
        
        # Create test data
        self.event_type = EventType.objects.create(name='Test Type')
        self.venue_category = VenueCategory.objects.create(name='Test Venue Category')
        self.venue = Venue.objects.create(
            name='Test Venue',
            category=self.venue_category,
            address='Test Address',
            city='Test City',
            state='Test State',
            country='IN',
            capacity_min=10,
            capacity_max=100,
            base_price=Decimal('5000.00'),
            description='Test venue'
        )
        
    def test_event_browsing(self):
        """Test event browsing functionality"""
        # Event list loads
        response = self.client.get('/events/')
        self.assertEqual(response.status_code, 200)
        
        # Event categories load
        response = self.client.get('/events/categories/')
        self.assertEqual(response.status_code, 200)
        
        # Category pages load
        for category in ['sports', 'music', 'cooking', 'coding', 'adventure', 'movie']:
            response = self.client.get(f'/events/{category}/')
            self.assertEqual(response.status_code, 200, f'{category} events page failed')
            
    def test_my_events_page(self):
        """Test my events page"""
        response = self.client.get('/users/my-events/')
        self.assertEqual(response.status_code, 200)

class VenuesSmokeTests(TestCase):
    """Test venue browsing and booking"""
    
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='venuetest',
            email='venue@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='venue@example.com', password='testpass123')
        
        # Create test venue
        self.venue_category = VenueCategory.objects.create(name='Test Category')
        self.venue = Venue.objects.create(
            name='Test Venue',
            slug='test-venue-123',
            category=self.venue_category,
            address='123 Test Street',
            city='Test City',
            state='Test State',
            country='IN',
            capacity_min=50,
            capacity_max=500,
            base_price=Decimal('10000.00'),
            description='Test venue for events'
        )
        
    def test_venue_browsing(self):
        """Test venue browsing functionality"""
        # Venue list loads
        response = self.client.get('/venues/')
        self.assertEqual(response.status_code, 200)
        
        # Venue detail loads
        response = self.client.get(f'/venues/{self.venue.slug}/')
        self.assertEqual(response.status_code, 200)
        
        # Venue gallery loads
        response = self.client.get(f'/venues/{self.venue.slug}/gallery/')
        self.assertEqual(response.status_code, 200)
        
        # Venue booking loads
        response = self.client.get(f'/venues/{self.venue.slug}/book/')
        self.assertEqual(response.status_code, 200)

class ManagersSmokeTests(TestCase):
    """Test manager functionality"""
    
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='managertest',
            email='managertest@example.com',
            password='testpass123'
        )
        self.manager = CustomUser.objects.create_user(
            username='testmanager',
            email='testmanager@example.com',
            password='testpass123',
            user_type='manager'
        )
        self.client = Client()
        self.client.login(username='managertest@example.com', password='testpass123')
        
    def test_manager_directory(self):
        """Test manager directory and profiles"""
        # Manager list loads
        response = self.client.get('/managers/')
        self.assertEqual(response.status_code, 200)
        
        # Manager detail loads
        response = self.client.get(f'/managers/{self.manager.id}/')
        self.assertEqual(response.status_code, 200)
        
        # Manager contact loads
        response = self.client.get(f'/managers/contact/{self.manager.id}/')
        self.assertEqual(response.status_code, 200)

class PaymentsSmokeTests(TestCase):
    """Test payment functionality"""
    
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='paymenttest',
            email='payment@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='payment@example.com', password='testpass123')
        
        # Create payment method
        self.payment_method = PaymentMethod.objects.create(
            name='test_method',
            payment_type='credit_card'
        )
        
    def test_payment_pages(self):
        """Test payment-related pages"""
        # Payment list loads
        response = self.client.get('/payments/')
        self.assertEqual(response.status_code, 200)

class CommunicationsSmokeTests(TestCase):
    """Test communication functionality"""
    
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='commtest',
            email='comm@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='comm@example.com', password='testpass123')
        
    def test_communication_pages(self):
        """Test communication pages"""
        # Inbox loads
        response = self.client.get('/communications/')
        self.assertEqual(response.status_code, 200)
        
        # Conversations load
        response = self.client.get('/communications/conversations/')
        self.assertEqual(response.status_code, 200)

class PublicPagesSmokeTests(TestCase):
    """Test public pages"""
    
    def setUp(self):
        self.client = Client()
        
    def test_public_pages(self):
        """Test all public pages load"""
        public_pages = [
            '/',
            '/about/',
            '/contact/', 
            '/gallery/',
            '/pricing/',
            '/faq/',
            '/privacy/',
            '/terms/',
            '/ai-mood-designer/'
        ]
        
        for page in public_pages:
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertEqual(response.status_code, 200, f'Page {page} failed to load')

class APISmokeTests(TestCase):
    """Test API endpoints"""
    
    def setUp(self):
        self.client = Client()
        
    def test_api_endpoints(self):
        """Test API endpoints respond correctly"""
        api_endpoints = [
            '/api/users/',
            '/api/events/',
            '/api/venues/',
            '/api/managers/',
            '/api/payments/'
        ]
        
        for endpoint in api_endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.client.get(endpoint)
                self.assertIn(response.status_code, [200, 401, 403], f'API {endpoint} failed')

class DashboardSmokeTests(TestCase):
    """Test dashboard functionality for different user types"""
    
    def test_user_dashboard(self):
        """Test user dashboard"""
        user = CustomUser.objects.create_user(
            username='dashtest',
            email='dash@example.com',
            password='testpass123',
            user_type='user'
        )
        
        client = Client()
        client.login(username='dash@example.com', password='testpass123')
        
        response = client.get('/users/dashboard/')
        self.assertEqual(response.status_code, 200)
        
    def test_manager_dashboard(self):
        """Test manager dashboard"""
        manager = CustomUser.objects.create_user(
            username='managerdash',
            email='managerdash@example.com',
            password='testpass123',
            user_type='manager'
        )
        
        client = Client()
        client.login(username='managerdash@example.com', password='testpass123')
        
        response = client.get('/users/dashboard/manager/')
        self.assertEqual(response.status_code, 200)
        
    def test_admin_dashboard(self):
        """Test admin dashboard"""
        admin = CustomUser.objects.create_user(
            username='admindash',
            email='admindash@example.com',
            password='testpass123',
            user_type='admin'
        )
        
        client = Client()
        client.login(username='admindash@example.com', password='testpass123')
        
        response = client.get('/users/dashboard/admin/')
        self.assertEqual(response.status_code, 200)

class AIFeaturesSmokeTests(TestCase):
    """Test AI features"""
    
    def setUp(self):
        self.client = Client()
        
    def test_ai_chatbot(self):
        """Test AI chatbot functionality"""
        response = self.client.post('/ai-chatbot/process/', 
            data=json.dumps({'message': 'hello'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Check response contains expected fields
        data = response.json()
        self.assertIn('success', data)
        self.assertIn('response', data)

class ExportSmokeTests(TestCase):
    """Test export functionality"""
    
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='exporttest',
            email='export@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='export@example.com', password='testpass123')
        
    def test_payment_export(self):
        """Test payment export functionality"""
        response = self.client.get('/payments/export/')
        self.assertIn(response.status_code, [200, 302])  # Success or redirect
