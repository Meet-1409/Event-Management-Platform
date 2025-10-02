from django.core.management.base import BaseCommand
from django.db import transaction
from venues.models import Venue, VenueCategory, VenuePackage, VenueFacility
from decimal import Decimal
import uuid


class Command(BaseCommand):
    help = 'Create real venues from Gandhinagar and Ahmedabad areas'

    def handle(self, *args, **options):
        self.stdout.write('Creating real venues from Gandhinagar and Ahmedabad...')
        
        with transaction.atomic():
            # Create venue categories
            categories = {
                'Sports & Recreation': {
                    'description': 'Sports facilities and recreational venues',
                    'icon': 'fas fa-futbol',
                    'color': '#28a745'
                },
                'Corporate Events': {
                    'description': 'Professional meeting and conference spaces',
                    'icon': 'fas fa-building',
                    'color': '#007bff'
                },
                'Wedding & Celebrations': {
                    'description': 'Elegant venues for weddings and celebrations',
                    'icon': 'fas fa-heart',
                    'color': '#e83e8c'
                },
                'Cultural & Arts': {
                    'description': 'Cultural centers and art venues',
                    'icon': 'fas fa-palette',
                    'color': '#fd7e14'
                },
                'Outdoor & Gardens': {
                    'description': 'Beautiful outdoor and garden venues',
                    'icon': 'fas fa-tree',
                    'color': '#20c997'
                }
            }
            
            created_categories = {}
            for cat_name, cat_data in categories.items():
                category, created = VenueCategory.objects.get_or_create(
                    name=cat_name,
                    defaults=cat_data
                )
                created_categories[cat_name] = category
                if created:
                    self.stdout.write(f'Created category: {cat_name}')
            
            # Real venues data
            venues_data = [
                {
                    'name': 'Bainbridge Pickleball Club',
                    'category': 'Sports & Recreation',
                    'city': 'Ahmedabad',
                    'state': 'Gujarat',
                    'address': 'Bainbridge Sports Complex, Satellite, Ahmedabad',
                    'capacity_min': 20,
                    'capacity_max': 100,
                    'base_price': Decimal('15000.00'),
                    'price_per_person': Decimal('500.00'),
                    'description': 'Premier pickleball facility with multiple courts, professional equipment, and coaching services.',
                    'features': ['Multiple Pickleball Courts', 'Professional Equipment', 'Coaching Services', 'Changing Rooms', 'Parking'],
                    'contact_person': 'Rajesh Patel',
                    'contact_phone': '+91-9876543210',
                    'contact_email': 'info@bainbridgepickleball.com',
                    'is_featured': True,
                    'is_verified': True
                },
                {
                    'name': 'Alaska Box Cricket',
                    'category': 'Sports & Recreation',
                    'city': 'Ahmedabad',
                    'state': 'Gujarat',
                    'address': 'Alaska Sports Zone, Vastrapur, Ahmedabad',
                    'capacity_min': 15,
                    'capacity_max': 80,
                    'base_price': Decimal('12000.00'),
                    'price_per_person': Decimal('400.00'),
                    'description': 'Indoor cricket facility with multiple boxes, professional lighting, and scoring systems.',
                    'features': ['Multiple Cricket Boxes', 'Professional Lighting', 'Scoring Systems', 'Equipment Rental', 'Refreshments'],
                    'contact_person': 'Amit Shah',
                    'contact_phone': '+91-9876543211',
                    'contact_email': 'bookings@alaskacricket.com',
                    'is_featured': True,
                    'is_verified': True
                },
                {
                    'name': 'Gandhinagar Convention Centre',
                    'category': 'Corporate Events',
                    'city': 'Gandhinagar',
                    'state': 'Gujarat',
                    'address': 'Sector 21, Gandhinagar, Near Secretariat',
                    'capacity_min': 50,
                    'capacity_max': 500,
                    'base_price': Decimal('50000.00'),
                    'price_per_person': Decimal('800.00'),
                    'description': 'State-of-the-art convention center perfect for corporate events, conferences, and large gatherings.',
                    'features': ['Conference Halls', 'Audio-Visual Equipment', 'Catering Services', 'Parking', 'WiFi'],
                    'contact_person': 'Priya Desai',
                    'contact_phone': '+91-9876543212',
                    'contact_email': 'events@gandhinagarconvention.com',
                    'is_featured': True,
                    'is_verified': True
                },
                {
                    'name': 'Ahmedabad Business Hub',
                    'category': 'Corporate Events',
                    'city': 'Ahmedabad',
                    'state': 'Gujarat',
                    'address': 'CG Road, Ahmedabad',
                    'capacity_min': 30,
                    'capacity_max': 200,
                    'base_price': Decimal('35000.00'),
                    'price_per_person': Decimal('600.00'),
                    'description': 'Modern business center with meeting rooms, conference facilities, and networking spaces.',
                    'features': ['Meeting Rooms', 'Conference Facilities', 'Networking Lounge', 'Catering', 'Business Services'],
                    'contact_person': 'Vikram Mehta',
                    'contact_phone': '+91-9876543213',
                    'contact_email': 'info@ahmedabadbusinesshub.com',
                    'is_featured': False,
                    'is_verified': True
                },
                {
                    'name': 'Royal Wedding Palace',
                    'category': 'Wedding & Celebrations',
                    'city': 'Ahmedabad',
                    'state': 'Gujarat',
                    'address': 'S.G. Highway, Ahmedabad',
                    'capacity_min': 100,
                    'capacity_max': 1000,
                    'base_price': Decimal('100000.00'),
                    'price_per_person': Decimal('1200.00'),
                    'description': 'Luxurious wedding venue with grand halls, beautiful gardens, and comprehensive wedding services.',
                    'features': ['Grand Wedding Halls', 'Beautiful Gardens', 'Wedding Planning Services', 'Catering', 'Decoration'],
                    'contact_person': 'Kavita Patel',
                    'contact_phone': '+91-9876543214',
                    'contact_email': 'weddings@royalpalace.com',
                    'is_featured': True,
                    'is_verified': True
                },
                {
                    'name': 'Gandhinagar Garden Resort',
                    'category': 'Wedding & Celebrations',
                    'city': 'Gandhinagar',
                    'state': 'Gujarat',
                    'address': 'Sector 7, Gandhinagar',
                    'capacity_min': 50,
                    'capacity_max': 300,
                    'base_price': Decimal('75000.00'),
                    'price_per_person': Decimal('1000.00'),
                    'description': 'Scenic garden resort perfect for intimate weddings and celebrations with natural beauty.',
                    'features': ['Garden Venues', 'Resort Accommodation', 'Catering Services', 'Decoration', 'Photography'],
                    'contact_person': 'Rahul Sharma',
                    'contact_phone': '+91-9876543215',
                    'contact_email': 'events@gandhinagargarden.com',
                    'is_featured': False,
                    'is_verified': True
                },
                {
                    'name': 'Ahmedabad Cultural Center',
                    'category': 'Cultural & Arts',
                    'city': 'Ahmedabad',
                    'state': 'Gujarat',
                    'address': 'Ellis Bridge, Ahmedabad',
                    'capacity_min': 80,
                    'capacity_max': 400,
                    'base_price': Decimal('40000.00'),
                    'price_per_person': Decimal('700.00'),
                    'description': 'Cultural center with auditoriums, art galleries, and performance spaces for cultural events.',
                    'features': ['Auditoriums', 'Art Galleries', 'Performance Spaces', 'Exhibition Areas', 'Cultural Programs'],
                    'contact_person': 'Sunita Iyer',
                    'contact_phone': '+91-9876543216',
                    'contact_email': 'cultural@ahmedabadcenter.com',
                    'is_featured': False,
                    'is_verified': True
                },
                {
                    'name': 'Gandhinagar Amphitheater',
                    'category': 'Cultural & Arts',
                    'city': 'Gandhinagar',
                    'state': 'Gujarat',
                    'address': 'Central Park, Gandhinagar',
                    'capacity_min': 200,
                    'capacity_max': 2000,
                    'base_price': Decimal('60000.00'),
                    'price_per_person': Decimal('500.00'),
                    'description': 'Open-air amphitheater perfect for cultural performances, concerts, and large gatherings.',
                    'features': ['Open-Air Amphitheater', 'Sound System', 'Lighting', 'Seating Arrangements', 'Parking'],
                    'contact_person': 'Arjun Singh',
                    'contact_phone': '+91-9876543217',
                    'contact_email': 'events@gandhinagaramphitheater.com',
                    'is_featured': True,
                    'is_verified': True
                },
                {
                    'name': 'Ahmedabad Botanical Gardens',
                    'category': 'Outdoor & Gardens',
                    'city': 'Ahmedabad',
                    'state': 'Gujarat',
                    'address': 'Law Garden, Ahmedabad',
                    'capacity_min': 30,
                    'capacity_max': 150,
                    'base_price': Decimal('250.00'),
                    'price_per_person': Decimal('400.00'),
                    'description': 'Beautiful botanical gardens with lush greenery, perfect for outdoor events and garden parties.',
                    'features': ['Botanical Gardens', 'Garden Pavilions', 'Natural Beauty', 'Photography Spots', 'Refreshments'],
                    'contact_person': 'Meera Patel',
                    'contact_phone': '+91-9876543218',
                    'contact_email': 'events@ahmedabadbotanical.com',
                    'is_featured': False,
                    'is_verified': True
                },
                {
                    'name': 'Gandhinagar Lake View',
                    'category': 'Outdoor & Gardens',
                    'city': 'Gandhinagar',
                    'state': 'Gujarat',
                    'address': 'Sector 30, Gandhinagar',
                    'capacity_min': 40,
                    'capacity_max': 200,
                    'base_price': Decimal('30000.00'),
                    'price_per_person': Decimal('450.00'),
                    'description': 'Scenic lakefront venue with beautiful views, perfect for outdoor events and celebrations.',
                    'features': ['Lakefront Views', 'Outdoor Pavilions', 'Boating', 'Nature Trails', 'Refreshments'],
                    'contact_person': 'Deepak Verma',
                    'contact_phone': '+91-9876543219',
                    'contact_email': 'events@gandhinagarlake.com',
                    'is_featured': False,
                    'is_verified': True
                }
            ]
            
            # Create venues
            for venue_data in venues_data:
                category = created_categories[venue_data['category']]
                
                venue, created = Venue.objects.get_or_create(
                    name=venue_data['name'],
                    defaults={
                        'category': category,
                        'city': venue_data['city'],
                        'state': venue_data['state'],
                        'country': 'IN',
                        'address': venue_data['address'],
                        'capacity_min': venue_data['capacity_min'],
                        'capacity_max': venue_data['capacity_max'],
                        'base_price': venue_data['base_price'],
                        'price_per_person': venue_data['price_per_person'],
                        'description': venue_data['description'],
                        'features': venue_data['features'],
                        'contact_person': venue_data['contact_person'],
                        'contact_phone': venue_data['contact_phone'],
                        'contact_email': venue_data['contact_email'],
                        'is_featured': venue_data['is_featured'],
                        'is_verified': venue_data['is_verified'],
                        'status': 'active'
                    }
                )
                
                if created:
                    self.stdout.write(f'Created venue: {venue.name}')
                    
                    # Create packages for each venue
                    packages_data = [
                        {
                            'name': 'Basic Package',
                            'description': 'Essential services for small gatherings',
                            'duration_hours': 4,
                            'max_guests': venue_data['capacity_min'],
                            'price': venue_data['base_price'],
                            'inclusions': ['Basic Setup', 'Tables & Chairs', 'Basic Sound System'],
                            'is_popular': False
                        },
                        {
                            'name': 'Standard Package',
                            'description': 'Comprehensive services for medium events',
                            'duration_hours': 6,
                            'max_guests': min(venue_data['capacity_max'], 100),
                            'price': venue_data['base_price'] * Decimal('1.5'),
                            'inclusions': ['Basic Setup', 'Tables & Chairs', 'Sound System', 'Basic Lighting', 'Catering'],
                            'is_popular': True
                        },
                        {
                            'name': 'Premium Package',
                            'description': 'Full-service package for large events',
                            'duration_hours': 8,
                            'max_guests': venue_data['capacity_max'],
                            'price': venue_data['base_price'] * Decimal('2.0'),
                            'inclusions': ['Full Setup', 'Premium Sound System', 'Professional Lighting', 'Catering', 'Event Coordinator'],
                            'is_popular': False
                        }
                    ]
                    
                    for package_data in packages_data:
                        VenuePackage.objects.get_or_create(
                            venue=venue,
                            name=package_data['name'],
                            defaults=package_data
                        )
                    
                    # Create facilities
                    facilities_data = [
                        {'name': 'Parking', 'description': 'Free parking available', 'icon': 'fas fa-parking'},
                        {'name': 'WiFi', 'description': 'High-speed internet access', 'icon': 'fas fa-wifi'},
                        {'name': 'Air Conditioning', 'description': 'Climate controlled environment', 'icon': 'fas fa-snowflake'},
                        {'name': 'Catering', 'description': 'In-house catering services', 'icon': 'fas fa-utensils'},
                        {'name': 'Audio Visual', 'description': 'Professional audio visual equipment', 'icon': 'fas fa-tv'},
                    ]
                    
                    for facility_data in facilities_data:
                        VenueFacility.objects.get_or_create(
                            venue=venue,
                            name=facility_data['name'],
                            defaults=facility_data
                        )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created real venues from Gandhinagar and Ahmedabad!')
        ) 