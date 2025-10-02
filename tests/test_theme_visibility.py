"""
Theme Visibility Tests for 360° Event Manager
Ensures sage + white theme with black text everywhere
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from users.models import CustomUser
from bs4 import BeautifulSoup
import re

User = get_user_model()

class ThemeVisibilityTests(TestCase):
    """Test theme visibility and color compliance"""
    
    def setUp(self):
        # Create test users for different roles
        self.regular_user = CustomUser.objects.create_user(
            username='themeuser',
            email='theme@example.com',
            password='testpass123',
            user_type='user'
        )
        
        self.manager = CustomUser.objects.create_user(
            username='thememanager',
            email='manager@example.com',
            password='testpass123',
            user_type='manager'
        )
        
        self.admin = CustomUser.objects.create_user(
            username='themeadmin',
            email='admin@example.com',
            password='testpass123',
            user_type='admin'
        )
    
    def test_no_text_white_classes(self):
        """Test that no pages contain text-white classes"""
        client = Client()
        
        pages = ['/', '/gallery/', '/about/', '/events/', '/venues/', '/managers/']
        
        for page in pages:
            with self.subTest(page=page):
                response = client.get(page)
                if response.status_code == 200:
                    content = response.content.decode()
                    self.assertNotIn('text-white', content, f"Found text-white class in {page}")
    
    def test_no_gradients(self):
        """Test that no pages contain linear-gradient in content"""
        client = Client()
        
        pages = ['/', '/gallery/', '/about/']
        
        for page in pages:
            with self.subTest(page=page):
                response = client.get(page)
                if response.status_code == 200:
                    content = response.content.decode()
                    # Allow gradients only in CSS variables, not inline styles
                    inline_gradients = re.findall(r'style="[^"]*linear-gradient[^"]*"', content)
                    self.assertEqual(len(inline_gradients), 0, 
                        f"Found inline gradients in {page}: {inline_gradients}")
    
    def test_no_dead_links(self):
        """Test that no pages contain href='#' links"""
        client = Client()
        
        pages = ['/', '/events/', '/venues/', '/managers/']
        
        for page in pages:
            with self.subTest(page=page):
                response = client.get(page)
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
                        f"Found {len(actual_dead_links)} dead links in {page}")
    
    def test_theme_css_loaded(self):
        """Test that theme.css is loaded in base template"""
        client = Client()
        response = client.get('/')
        
        if response.status_code == 200:
            content = response.content.decode()
            self.assertIn('theme.css', content, "theme.css not loaded in base template")
    
    def test_buttons_use_theme_classes(self):
        """Test that buttons use .btn class and not custom color classes"""
        client = Client()
        
        pages = ['/', '/events/', '/venues/']
        
        for page in pages:
            with self.subTest(page=page):
                response = client.get(page)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    buttons = soup.find_all(['a', 'button'], class_=re.compile(r'.*btn.*'))
                    
                    for button in buttons:
                        classes = button.get('class', [])
                        # Should have 'btn' class
                        self.assertIn('btn', classes, f"Button missing .btn class in {page}")
    
    def test_dashboard_pages_render(self):
        """Test all dashboard pages render with sage theme"""
        # Test manager dashboards
        client = Client()
        client.login(username='manager@example.com', password='testpass123')
        
        manager_pages = [
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
                
                if response.status_code == 200:
                    content = response.content.decode()
                    # Should not contain text-white
                    self.assertNotIn('text-white', content)
        
        # Test admin dashboards
        client.login(username='admin@example.com', password='testpass123')
        
        admin_pages = [
            '/dashboard/admin/',
            '/dashboard/admin/users/',
            '/dashboard/admin/managers/',
            '/dashboard/admin/venues/',
            '/dashboard/admin/events/',
            '/dashboard/admin/payments/'
        ]
        
        for page in admin_pages:
            with self.subTest(page=page):
                response = client.get(page)
                self.assertIn(response.status_code, [200, 302])
    
    def test_chat_visibility(self):
        """Test chat components have proper visibility"""
        client = Client()
        client.login(username='theme@example.com', password='testpass123')
        
        response = client.get('/communications/')
        self.assertIn(response.status_code, [200, 302])
        
        if response.status_code == 200:
            content = response.content.decode()
            # Should not have dark chat bubbles or white text
            self.assertNotIn('text-white', content)
            self.assertNotIn('bg-dark', content)
    
    def test_no_invisible_text(self):
        """Test that no text is invisible due to poor contrast"""
        client = Client()
        
        # Test key pages
        pages = ['/', '/gallery/', '/about/', '/events/']
        
        for page in pages:
            with self.subTest(page=page):
                response = client.get(page)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for potentially invisible text combinations
                    white_on_white = soup.find_all(attrs={"style": re.compile(r'color:\s*white.*background.*white', re.I)})
                    light_on_light = soup.find_all(attrs={"style": re.compile(r'color:\s*#f.*background.*#f', re.I)})
                    
                    self.assertEqual(len(white_on_white), 0, f"Found white-on-white text in {page}")
                    self.assertEqual(len(light_on_light), 0, f"Found light-on-light text in {page}")

class SageColorComplianceTests(TestCase):
    """Test that only sage green and white colors are used"""
    
    def test_no_forbidden_colors(self):
        """Test that no forbidden colors appear in rendered pages"""
        client = Client()
        
        # Create test user and login
        user = CustomUser.objects.create_user(
            username='colortest',
            email='color@example.com',
            password='testpass123'
        )
        client.login(username='color@example.com', password='testpass123')
        
        pages = ['/', '/events/', '/venues/', '/managers/', '/users/dashboard/']
        
        # Forbidden color patterns (hex codes for common colors)
        forbidden_patterns = [
            r'#[0-9a-fA-F]*[0-9a-fA-F][bB][fF]',  # Blue variants
            r'#[fF][fF][0-9a-fA-F]*[0-9a-fA-F][0-9a-fA-F][0-9a-fA-F]',  # Red variants  
            r'#[fF][fF][fF][0-9a-fA-F]*[0-9a-fA-F][0-9a-fA-F]',  # Yellow variants
            r'#[8-9a-fA-F][0-9a-fA-F][0-9a-fA-F][8-9a-fA-F][0-9a-fA-F][0-9a-fA-F]'  # Purple variants
        ]
        
        for page in pages:
            with self.subTest(page=page):
                response = client.get(page)
                if response.status_code == 200:
                    content = response.content.decode()
                    
                    for pattern in forbidden_patterns:
                        matches = re.findall(pattern, content)
                        # Filter out sage green variants (should start with #6, #7, #8 for greens)
                        non_sage_matches = [m for m in matches if not re.match(r'#[6-8][a-fA-F0-9]', m)]
                        
                        self.assertEqual(len(non_sage_matches), 0, 
                            f"Found forbidden colors in {page}: {non_sage_matches}")

class ComponentVisibilityTests(TestCase):
    """Test specific component visibility"""
    
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='comptest',
            email='comp@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='comp@example.com', password='testpass123')
    
    def test_navigation_visibility(self):
        """Test navigation has proper contrast"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        navbar = soup.find('nav', class_='navbar')
        
        if navbar:
            # Should not have dark background with white text
            self.assertNotIn('navbar-dark', str(navbar))
            self.assertNotIn('bg-dark', str(navbar))
    
    def test_card_visibility(self):
        """Test cards have proper visibility"""
        response = self.client.get('/events/')
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            cards = soup.find_all('div', class_=re.compile(r'.*card.*'))
            
            for card in cards:
                card_style = card.get('style', '')
                # Should not have dark backgrounds
                self.assertNotIn('background: #1', card_style)
                self.assertNotIn('background: #2', card_style)
                self.assertNotIn('background: #3', card_style)
    
    def test_button_visibility(self):
        """Test buttons have proper visibility"""
        pages = ['/', '/events/', '/venues/']
        
        for page in pages:
            with self.subTest(page=page):
                response = self.client.get(page)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    buttons = soup.find_all(['a', 'button'], class_=re.compile(r'.*btn.*'))
                    
                    for button in buttons:
                        # Should have proper contrast
                        style = button.get('style', '')
                        self.assertNotIn('color: white', style)
                        self.assertNotIn('background: dark', style)
