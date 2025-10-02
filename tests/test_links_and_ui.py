"""
UI and Link Quality Tests for 360° Event Manager
Tests that all links work and UI is consistent
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse, NoReverseMatch
from users.models import CustomUser
from events.models import Event, EventType
from venues.models import Venue, VenueCategory
from bs4 import BeautifulSoup
import re

User = get_user_model()

class LinkQualityTests(TestCase):
    """Test that all links work and no dead anchors exist"""
    
    def setUp(self):
        # Create test users for different roles
        self.regular_user = CustomUser.objects.create_user(
            username='testuser',
            email='user@example.com',
            password='testpass123',
            user_type='user'
        )
        
        self.manager = CustomUser.objects.create_user(
            username='testmanager',
            email='manager@example.com',
            password='testpass123',
            user_type='manager'
        )
        
        self.admin = CustomUser.objects.create_user(
            username='testadmin',
            email='admin@example.com',
            password='testpass123',
            user_type='admin'
        )
        
        # Create test data
        self.venue_category = VenueCategory.objects.create(name='Test Category')
        self.venue = Venue.objects.create(
            name='Test Venue',
            slug='test-venue-123',
            category=self.venue_category,
            address='123 Test St',
            city='Test City',
            state='Test State',
            country='IN',
            capacity_min=50,
            capacity_max=500,
            base_price=10000,
            description='Test venue'
        )
        
        self.event_type = EventType.objects.create(name='Test Event Type')
        self.event = Event.objects.create(
            title='Test Event',
            description='Test event description',
            event_type=self.event_type,
            start_date='2024-12-25',
            end_date='2024-12-25',
            start_time='10:00',
            end_time='18:00',
            expected_guests=100,
            venue=self.venue,
            organizer=self.manager,
            total_budget=20000,
            venue_cost=10000,
            total_cost=20000,
            status='confirmed'
        )
    
    def test_public_pages_no_dead_links(self):
        """Test public pages have no href='#' links"""
        client = Client()
        
        public_pages = [
            '/',
            '/about/',
            '/contact/',
            '/gallery/',
            '/pricing/',
            '/faq/',
            '/ai-mood-designer/'
        ]
        
        for page in public_pages:
            with self.subTest(page=page):
                response = client.get(page)
                self.assertEqual(response.status_code, 200)
                
                # Parse HTML and check for dead links
                soup = BeautifulSoup(response.content, 'html.parser')
                dead_links = soup.find_all('a', href='#')
                
                # Filter out dropdown toggles and legitimate anchors
                actual_dead_links = [
                    link for link in dead_links 
                    if 'dropdown-toggle' not in link.get('class', []) and
                       'data-bs-toggle' not in link.attrs
                ]
                
                self.assertEqual(len(actual_dead_links), 0, 
                    f"Found {len(actual_dead_links)} dead links in {page}")
    
    def test_authenticated_pages_no_dead_links(self):
        """Test authenticated pages have no dead links"""
        client = Client()
        client.login(username='user@example.com', password='testpass123')
        
        authenticated_pages = [
            '/events/',
            '/venues/',
            '/managers/',
            '/payments/',
            '/communications/',
            '/users/dashboard/',
            '/users/profile/'
        ]
        
        for page in authenticated_pages:
            with self.subTest(page=page):
                response = client.get(page)
                self.assertIn(response.status_code, [200, 302])
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    dead_links = soup.find_all('a', href='#')
                    
                    # Filter out legitimate dropdown toggles
                    actual_dead_links = [
                        link for link in dead_links 
                        if 'dropdown-toggle' not in link.get('class', []) and
                           'data-bs-toggle' not in link.attrs
                    ]
                    
                    self.assertEqual(len(actual_dead_links), 0, 
                        f"Found dead links in {page}")
    
    def test_manager_dashboard_links(self):
        """Test manager dashboard has working links"""
        client = Client()
        client.login(username='manager@example.com', password='testpass123')
        
        manager_pages = [
            '/users/dashboard/',
            '/dashboard/manager/',
            '/dashboard/manager/events/',
            '/dashboard/manager/clients/',
            '/dashboard/manager/consultations/',
            '/dashboard/manager/earnings/'
        ]
        
        for page in manager_pages:
            with self.subTest(page=page):
                response = client.get(page)
                self.assertIn(response.status_code, [200, 302])
    
    def test_admin_dashboard_links(self):
        """Test admin dashboard has working links"""
        client = Client()
        client.login(username='admin@example.com', password='testpass123')
        
        admin_pages = [
            '/users/dashboard/',
            '/dashboard/admin/',
            '/dashboard/admin/users/',
            '/dashboard/admin/managers/',
            '/dashboard/admin/venues/',
            '/dashboard/admin/vendors/',
            '/dashboard/admin/events/',
            '/dashboard/admin/payments/',
            '/dashboard/admin/reports/'
        ]
        
        for page in admin_pages:
            with self.subTest(page=page):
                response = client.get(page)
                self.assertIn(response.status_code, [200, 302])

class URLReverseTests(TestCase):
    """Test that all {% url %} names in templates can be reversed"""
    
    def setUp(self):
        # Create minimal test data
        self.user = CustomUser.objects.create_user(
            username='urltest',
            email='url@example.com', 
            password='testpass123'
        )
        
    def test_url_names_reversible(self):
        """Test common URL names can be reversed"""
        # Common URL names used in templates
        url_names = [
            'home',
            'users:login',
            'users:register', 
            'users:profile',
            'users:dashboard',
            'events:event_list',
            'events:add_event',
            'events:event_categories',
            'venues:venue_list',
            'managers:manager_list',
            'payments:payment_list',
            'communications:inbox',
            'analytics:dashboard'
        ]
        
        for url_name in url_names:
            with self.subTest(url_name=url_name):
                try:
                    url = reverse(url_name)
                    self.assertIsNotNone(url)
                except NoReverseMatch:
                    self.fail(f"URL name '{url_name}' cannot be reversed")

class PlaceholderUniquenessTests(TestCase):
    """Test placeholder image uniqueness and category correctness"""
    
    def setUp(self):
        self.client = Client()
        
        # Create test events with different categories
        self.event_type_sports = EventType.objects.create(name='Sports')
        self.event_type_music = EventType.objects.create(name='Music')
        
        self.venue_category = VenueCategory.objects.create(name='Sports Complex')
        self.venue = Venue.objects.create(
            name='Test Venue',
            slug='test-venue',
            category=self.venue_category,
            address='123 Test St',
            city='Test City', 
            state='Test State',
            country='IN',
            capacity_min=50,
            capacity_max=500,
            base_price=10000,
            description='Test venue'
        )
        
        self.manager = CustomUser.objects.create_user(
            username='testmanager',
            email='manager@example.com',
            password='testpass123',
            user_type='manager'
        )
        
        # Create multiple events for testing
        for i in range(3):
            Event.objects.create(
                title=f'Sports Event {i+1}',
                description=f'Test sports event {i+1}',
                event_type=self.event_type_sports,
                start_date='2024-12-25',
                end_date='2024-12-25', 
                start_time='10:00',
                end_time='18:00',
                expected_guests=100,
                venue=self.venue,
                organizer=self.manager,
                total_budget=20000,
                venue_cost=10000,
                total_cost=20000,
                status='completed',
                is_public=True
            )
    
    def test_placeholder_uniqueness_on_gallery(self):
        """Test that gallery page has unique placeholder images"""
        response = self.client.get('/gallery/')
        self.assertEqual(response.status_code, 200)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        images = soup.find_all('img', src=re.compile(r'images\.unsplash\.com'))
        
        # Extract image URLs
        image_urls = [img['src'] for img in images]
        
        # Check uniqueness
        unique_urls = set(image_urls)
        self.assertEqual(len(image_urls), len(unique_urls), 
            "Found duplicate placeholder images on gallery page")
    
    def test_placeholder_category_correctness(self):
        """Test that placeholders match event categories"""
        from templates.templatetags.placeholders import placeholder_for
        
        # Test category mappings
        sports_url = placeholder_for('sports', 0)
        music_url = placeholder_for('music', 0)
        
        self.assertIn('sports', sports_url.lower())
        self.assertIn('music', music_url.lower())
        self.assertNotEqual(sports_url, music_url)

class DisabledElementTests(TestCase):
    """Test that no disabled buttons exist in user-facing pages"""
    
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='disabledtest',
            email='disabled@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='disabled@example.com', password='testpass123')
    
    def test_no_disabled_buttons(self):
        """Test that pages don't have disabled buttons"""
        pages_to_check = [
            '/events/',
            '/venues/',
            '/managers/',
            '/payments/',
            '/users/dashboard/'
        ]
        
        for page in pages_to_check:
            with self.subTest(page=page):
                response = self.client.get(page)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find disabled buttons
                    disabled_buttons = soup.find_all(['button', 'a'], class_=re.compile(r'.*disabled.*'))
                    disabled_buttons += soup.find_all(['button', 'a'], disabled=True)
                    
                    # Filter out legitimate disabled states (like form validation)
                    user_facing_disabled = [
                        btn for btn in disabled_buttons
                        if not any(cls in btn.get('class', []) for cls in ['form-control', 'pagination'])
                    ]
                    
                    self.assertEqual(len(user_facing_disabled), 0,
                        f"Found {len(user_facing_disabled)} disabled user-facing buttons in {page}")

class UIConsistencyTests(TestCase):
    """Test UI consistency across pages"""
    
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='uitest',
            email='ui@example.com',
            password='testpass123'
        )
        self.client.login(username='ui@example.com', password='testpass123')
    
    def test_consistent_navigation(self):
        """Test that navigation is consistent across pages"""
        pages = ['/events/', '/venues/', '/managers/']
        
        nav_structures = []
        for page in pages:
            response = self.client.get(page)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                nav = soup.find('nav', class_='navbar')
                if nav:
                    nav_links = [link.get('href') for link in nav.find_all('a')]
                    nav_structures.append(set(nav_links))
        
        # All pages should have similar navigation structure
        if len(nav_structures) > 1:
            base_nav = nav_structures[0]
            for nav in nav_structures[1:]:
                # Check that core navigation links are present
                common_links = base_nav.intersection(nav)
                self.assertGreater(len(common_links), 3, 
                    "Navigation structure varies too much between pages")
    
    def test_bootstrap_classes_consistent(self):
        """Test that Bootstrap classes are used consistently"""
        pages = ['/events/', '/venues/', '/managers/']
        
        for page in pages:
            with self.subTest(page=page):
                response = self.client.get(page)
                if response.status_code == 200:
                    content = response.content.decode()
                    
                    # Check for consistent Bootstrap usage
                    self.assertIn('btn btn-primary', content)
                    self.assertIn('card border-0 shadow-sm', content)
                    self.assertIn('container', content)

class TemplateRenderingTests(TestCase):
    """Test that all templates render without errors"""
    
    def setUp(self):
        self.users = {}
        for user_type in ['user', 'manager', 'admin']:
            self.users[user_type] = CustomUser.objects.create_user(
                username=f'test{user_type}',
                email=f'{user_type}@example.com',
                password='testpass123',
                user_type=user_type
            )
    
    def test_dashboard_templates_render(self):
        """Test all dashboard templates render correctly"""
        # Test manager dashboard templates
        client = Client()
        client.login(username='manager@example.com', password='testpass123')
        
        manager_pages = [
            '/dashboard/manager/events/',
            '/dashboard/manager/clients/',
            '/dashboard/manager/consultations/',
            '/dashboard/manager/earnings/'
        ]
        
        for page in manager_pages:
            with self.subTest(page=page):
                response = client.get(page)
                self.assertIn(response.status_code, [200, 302])
        
        # Test admin dashboard templates
        client.login(username='admin@example.com', password='testpass123')
        
        admin_pages = [
            '/dashboard/admin/users/',
            '/dashboard/admin/managers/',
            '/dashboard/admin/venues/',
            '/dashboard/admin/vendors/',
            '/dashboard/admin/events/',
            '/dashboard/admin/payments/',
            '/dashboard/admin/reports/'
        ]
        
        for page in admin_pages:
            with self.subTest(page=page):
                response = client.get(page)
                self.assertIn(response.status_code, [200, 302])
    
    def test_email_templates_exist(self):
        """Test that all email templates exist and can be rendered"""
        from django.template.loader import get_template
        
        email_templates = [
            'payments/emails/payment_confirmation.html',
            'payments/emails/payment_confirmation.txt',
            'payments/emails/payment_instructions.html', 
            'payments/emails/payment_instructions.txt',
            'payments/emails/payment_failure.html',
            'payments/emails/payment_failure.txt',
            'payments/emails/refund_confirmation.html',
            'payments/emails/refund_confirmation.txt',
            'payments/emails/refund_request.html',
            'payments/emails/refund_request.txt'
        ]
        
        for template_name in email_templates:
            with self.subTest(template=template_name):
                try:
                    template = get_template(template_name)
                    self.assertIsNotNone(template)
                except:
                    self.fail(f"Email template {template_name} not found or cannot be loaded")

class FormFunctionalityTests(TestCase):
    """Test that forms work correctly"""
    
    def setUp(self):
        self.client = Client()
        
    def test_registration_form_works(self):
        """Test user registration form functionality"""
        response = self.client.get('/users/register/')
        self.assertEqual(response.status_code, 200)
        
        # Test form submission
        response = self.client.post('/users/register/', {
            'username': 'formtest',
            'email': 'formtest@example.com',
            'first_name': 'Form',
            'last_name': 'Test', 
            'phone_number': '+919876543213',
            'password1': 'testpass123',
            'password2': 'testpass123'
        })
        
        # Should either succeed (200/302) or show validation errors (200)
        self.assertIn(response.status_code, [200, 302])
        
        # Check if user was created (if form was valid)
        if response.status_code == 302:
            self.assertTrue(CustomUser.objects.filter(username='formtest').exists())

class APIEndpointTests(TestCase):
    """Test API endpoint functionality"""
    
    def test_api_endpoints_respond(self):
        """Test that API endpoints respond correctly"""
        client = Client()
        
        api_endpoints = [
            '/api/users/',
            '/api/events/', 
            '/api/venues/',
            '/api/managers/',
            '/api/payments/'
        ]
        
        for endpoint in api_endpoints:
            with self.subTest(endpoint=endpoint):
                response = client.get(endpoint)
                # APIs should return 200 (success) or 401/403 (auth required)
                self.assertIn(response.status_code, [200, 401, 403])
                
                # Check JSON response
                if response.status_code == 200:
                    try:
                        data = response.json()
                        self.assertIsInstance(data, dict)
                    except:
                        self.fail(f"API {endpoint} did not return valid JSON")
