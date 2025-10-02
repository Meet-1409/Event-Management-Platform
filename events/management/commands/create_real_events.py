from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from events.models import Event, EventType
from venues.models import Venue
from users.models import CustomUser
from decimal import Decimal
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Create real events from Gandhinagar and Ahmedabad areas'

    def handle(self, *args, **options):
        self.stdout.write('Creating real events from Gandhinagar and Ahmedabad...')
        
        with transaction.atomic():
            # Create event types
            event_types = {
                'Sports Tournament': {
                    'description': 'Competitive sports events and tournaments',
                    'icon': 'fas fa-trophy',
                    'color': '#28a745'
                },
                'Corporate Meeting': {
                    'description': 'Business meetings and corporate events',
                    'icon': 'fas fa-briefcase',
                    'color': '#007bff'
                },
                'Cultural Festival': {
                    'description': 'Cultural celebrations and festivals',
                    'icon': 'fas fa-music',
                    'color': '#fd7e14'
                },
                'Workshop': {
                    'description': 'Educational workshops and training sessions',
                    'icon': 'fas fa-chalkboard-teacher',
                    'color': '#6f42c1'
                },
                'Birthday Party': {
                    'description': 'Private birthday celebrations',
                    'icon': 'fas fa-birthday-cake',
                    'color': '#e83e8c'
                },
                'Wedding Ceremony': {
                    'description': 'Wedding celebrations and ceremonies',
                    'icon': 'fas fa-heart',
                    'color': '#dc3545'
                }
            }
            
            created_types = {}
            for type_name, type_data in event_types.items():
                event_type, created = EventType.objects.get_or_create(
                    name=type_name,
                    defaults=type_data
                )
                created_types[type_name] = event_type
                if created:
                    self.stdout.write(f'Created event type: {type_name}')
            
            # Get or create a manager user
            manager, created = CustomUser.objects.get_or_create(
                email='manager@eventmanager.com',
                defaults={
                    'username': 'eventmanager',
                    'first_name': 'Event',
                    'last_name': 'Manager',
                    'user_type': 'manager',
                    'phone_number': '+91-9876543200',
                    'is_staff': True,
                    'is_active': True
                }
            )
            
            # Get venues
            venues = list(Venue.objects.filter(status='active'))
            if not venues:
                self.stdout.write('No active venues found. Please run create_real_venues first.')
                return
            
            # Real events data
            events_data = [
                # Public Events
                {
                    'title': 'Ahmedabad Pickleball Championship 2024',
                    'event_type': 'Sports Tournament',
                    'description': 'Annual pickleball championship featuring top players from Gujarat. Open to all skill levels with separate categories for beginners, intermediate, and advanced players.',
                    'sub_category': 'Pickleball',
                    'skill_level': 'All Levels',
                    'format': 'In-person',
                    'is_public': True,
                    'expected_guests': 150,
                    'total_budget': Decimal('275.00'),
                    'venue_cost': Decimal('250.00'),
                    'vendor_costs': Decimal('30000.00'),
                    'manager_fee': Decimal('5000.00'),
                    'total_cost': Decimal('275.00'),
                    'theme': 'Sports Championship',
                    'special_requirements': 'Professional pickleball equipment, referees, first aid station',
                    'tags': ['sports', 'pickleball', 'championship', 'tournament']
                },
                {
                    'title': 'Gujarat Tech Summit 2024',
                    'event_type': 'Corporate Meeting',
                    'description': 'Annual technology summit bringing together IT professionals, startups, and industry leaders from across Gujarat.',
                    'sub_category': 'Technology',
                    'skill_level': 'Professional',
                    'format': 'In-person',
                    'is_public': True,
                    'expected_guests': 300,
                    'total_budget': Decimal('295.00'),
                    'venue_cost': Decimal('80000.00'),
                    'vendor_costs': Decimal('80000.00'),
                    'manager_fee': Decimal('15000.00'),
                    'total_cost': Decimal('295.00'),
                    'theme': 'Technology Innovation',
                    'special_requirements': 'High-speed internet, presentation equipment, networking area',
                    'tags': ['technology', 'summit', 'corporate', 'networking']
                },
                {
                    'title': 'Ahmedabad Cricket League Finals',
                    'event_type': 'Sports Tournament',
                    'description': 'Championship finals of the Ahmedabad Cricket League featuring the top teams in an exciting showdown.',
                    'sub_category': 'Cricket',
                    'skill_level': 'Advanced',
                    'format': 'In-person',
                    'is_public': True,
                    'expected_guests': 200,
                    'total_budget': Decimal('280.00'),
                    'venue_cost': Decimal('35000.00'),
                    'vendor_costs': Decimal('45000.00'),
                    'manager_fee': Decimal('8000.00'),
                    'total_cost': Decimal('280.00'),
                    'theme': 'Cricket Championship',
                    'special_requirements': 'Professional cricket equipment, live streaming setup, commentary booth',
                    'tags': ['cricket', 'league', 'finals', 'sports']
                },
                {
                    'title': 'Gandhinagar Cultural Festival',
                    'event_type': 'Cultural Festival',
                    'description': 'Week-long cultural festival celebrating the rich heritage and arts of Gujarat with performances, exhibitions, and workshops.',
                    'sub_category': 'Cultural',
                    'skill_level': 'All Levels',
                    'format': 'In-person',
                    'is_public': True,
                    'expected_guests': 500,
                    'total_budget': Decimal('320.00'),
                    'venue_cost': Decimal('60000.00'),
                    'vendor_costs': Decimal('70000.00'),
                    'manager_fee': Decimal('12000.00'),
                    'total_cost': Decimal('320.00'),
                    'theme': 'Cultural Heritage',
                    'special_requirements': 'Multiple performance stages, art exhibition area, food stalls',
                    'tags': ['cultural', 'festival', 'heritage', 'arts']
                },
                {
                    'title': 'Digital Marketing Workshop',
                    'event_type': 'Workshop',
                    'description': 'Comprehensive workshop on digital marketing strategies, social media management, and online advertising.',
                    'sub_category': 'Marketing',
                    'skill_level': 'Intermediate',
                    'format': 'In-person',
                    'is_public': True,
                    'expected_guests': 80,
                    'total_budget': Decimal('220.00'),
                    'venue_cost': Decimal('15000.00'),
                    'vendor_costs': Decimal('20000.00'),
                    'manager_fee': Decimal('3000.00'),
                    'total_cost': Decimal('220.00'),
                    'theme': 'Digital Marketing',
                    'special_requirements': 'Projector, laptops for participants, high-speed internet',
                    'tags': ['workshop', 'marketing', 'digital', 'education']
                },
                {
                    'title': 'Ahmedabad Startup Meetup',
                    'event_type': 'Corporate Meeting',
                    'description': 'Monthly meetup for startup founders, investors, and entrepreneurs to network and share insights.',
                    'sub_category': 'Startup',
                    'skill_level': 'Professional',
                    'format': 'In-person',
                    'is_public': True,
                    'expected_guests': 120,
                    'total_budget': Decimal('35000.00'),
                    'venue_cost': Decimal('12000.00'),
                    'vendor_costs': Decimal('15000.00'),
                    'manager_fee': Decimal('25.00'),
                    'total_cost': Decimal('35000.00'),
                    'theme': 'Startup Networking',
                    'special_requirements': 'Networking area, presentation equipment, refreshments',
                    'tags': ['startup', 'networking', 'entrepreneurship', 'meetup']
                },
                {
                    'title': 'Gujarat Food Festival',
                    'event_type': 'Cultural Festival',
                    'description': 'Celebration of Gujarati cuisine featuring local chefs, food stalls, and cooking demonstrations.',
                    'sub_category': 'Food',
                    'skill_level': 'All Levels',
                    'format': 'In-person',
                    'is_public': True,
                    'expected_guests': 400,
                    'total_budget': Decimal('300.00'),
                    'venue_cost': Decimal('40000.00'),
                    'vendor_costs': Decimal('60000.00'),
                    'manager_fee': Decimal('10000.00'),
                    'total_cost': Decimal('300.00'),
                    'theme': 'Gujarati Cuisine',
                    'special_requirements': 'Kitchen facilities, food stalls, seating arrangements',
                    'tags': ['food', 'festival', 'gujarati', 'cuisine']
                },
                {
                    'title': 'Ahmedabad Yoga Workshop',
                    'event_type': 'Workshop',
                    'description': 'Wellness workshop focusing on yoga, meditation, and mindfulness practices for stress relief.',
                    'sub_category': 'Yoga',
                    'skill_level': 'Beginner',
                    'format': 'In-person',
                    'is_public': True,
                    'expected_guests': 60,
                    'total_budget': Decimal('250.00'),
                    'venue_cost': Decimal('8000.00'),
                    'vendor_costs': Decimal('12000.00'),
                    'manager_fee': Decimal('2000.00'),
                    'total_cost': Decimal('250.00'),
                    'theme': 'Wellness & Yoga',
                    'special_requirements': 'Yoga mats, meditation cushions, peaceful environment',
                    'tags': ['yoga', 'wellness', 'meditation', 'workshop']
                },
                
                # Private Events (Birthdays, Weddings)
                {
                    'title': 'Priya Patel Birthday Celebration',
                    'event_type': 'Birthday Party',
                    'description': 'Private birthday celebration for Priya Patel with family and close friends.',
                    'sub_category': 'Birthday',
                    'skill_level': 'All Levels',
                    'format': 'In-person',
                    'is_public': False,
                    'expected_guests': 50,
                    'total_budget': Decimal('35000.00'),
                    'venue_cost': Decimal('15000.00'),
                    'vendor_costs': Decimal('15000.00'),
                    'manager_fee': Decimal('25.00'),
                    'total_cost': Decimal('35000.00'),
                    'theme': 'Birthday Celebration',
                    'special_requirements': 'Birthday decorations, cake, entertainment',
                    'tags': ['birthday', 'celebration', 'private', 'family']
                },
                {
                    'title': 'Raj & Anjali Wedding Ceremony',
                    'event_type': 'Wedding Ceremony',
                    'description': 'Traditional Gujarati wedding ceremony celebrating the union of Raj and Anjali.',
                    'sub_category': 'Wedding',
                    'skill_level': 'All Levels',
                    'format': 'In-person',
                    'is_public': False,
                    'expected_guests': 300,
                    'total_budget': Decimal('350.00'),
                    'venue_cost': Decimal('150000.00'),
                    'vendor_costs': Decimal('250000.00'),
                    'manager_fee': Decimal('25000.00'),
                    'total_cost': Decimal('350.00'),
                    'theme': 'Traditional Wedding',
                    'special_requirements': 'Wedding mandap, traditional decorations, catering for 300 guests',
                    'tags': ['wedding', 'traditional', 'gujarati', 'ceremony']
                },
                {
                    'title': 'Amit Shah Birthday Party',
                    'event_type': 'Birthday Party',
                    'description': 'Private birthday party for Amit Shah with close friends and family.',
                    'sub_category': 'Birthday',
                    'skill_level': 'All Levels',
                    'format': 'In-person',
                    'is_public': False,
                    'expected_guests': 40,
                    'total_budget': Decimal('28000.00'),
                    'venue_cost': Decimal('12000.00'),
                    'vendor_costs': Decimal('12000.00'),
                    'manager_fee': Decimal('2000.00'),
                    'total_cost': Decimal('28000.00'),
                    'theme': 'Birthday Party',
                    'special_requirements': 'Party decorations, birthday cake, music system',
                    'tags': ['birthday', 'party', 'private', 'celebration']
                },
                {
                    'title': 'Vikram & Meera Wedding Reception',
                    'event_type': 'Wedding Ceremony',
                    'description': 'Wedding reception for Vikram and Meera with traditional and modern elements.',
                    'sub_category': 'Wedding',
                    'skill_level': 'All Levels',
                    'format': 'In-person',
                    'is_public': False,
                    'expected_guests': 250,
                    'total_budget': Decimal('340.00'),
                    'venue_cost': Decimal('120000.00'),
                    'vendor_costs': Decimal('200000.00'),
                    'manager_fee': Decimal('20000.00'),
                    'total_cost': Decimal('340.00'),
                    'theme': 'Modern Wedding Reception',
                    'special_requirements': 'Reception setup, professional catering, entertainment',
                    'tags': ['wedding', 'reception', 'modern', 'celebration']
                }
            ]
            
            # Create events with dates spread over the next few months
            base_date = date.today()
            for i, event_data in enumerate(events_data):
                # Spread events over the next 3 months
                event_date = base_date + timedelta(days=random.randint(7, 90))
                
                # Select appropriate venue based on event type
                if 'Sports' in event_data['event_type'] or 'Cricket' in event_data['title'] or 'Pickleball' in event_data['title']:
                    venue = random.choice([v for v in venues if 'Sports' in v.category.name or 'sport' in v.name.lower()])
                elif 'Corporate' in event_data['event_type'] or 'Meeting' in event_data['title'] or 'Summit' in event_data['title']:
                    venue = random.choice([v for v in venues if 'Corporate' in v.category.name])
                elif 'Wedding' in event_data['event_type'] or 'Wedding' in event_data['title']:
                    venue = random.choice([v for v in venues if 'Wedding' in v.category.name])
                elif 'Cultural' in event_data['event_type'] or 'Festival' in event_data['title']:
                    venue = random.choice([v for v in venues if 'Cultural' in v.category.name or 'Garden' in v.category.name])
                else:
                    venue = random.choice(venues)
                
                event_type = created_types[event_data['event_type']]
                
                event, created = Event.objects.get_or_create(
                    title=event_data['title'],
                    defaults={
                        'event_type': event_type,
                        'description': event_data['description'],
                        'sub_category': event_data['sub_category'],
                        'skill_level': event_data['skill_level'],
                        'format': event_data['format'],
                        'is_public': event_data['is_public'],
                        'start_date': event_date,
                        'end_date': event_date,
                        'start_time': timezone.now().replace(hour=10, minute=0, second=0, microsecond=0).time(),
                        'end_time': timezone.now().replace(hour=18, minute=0, second=0, microsecond=0).time(),
                        'expected_guests': event_data['expected_guests'],
                        'venue': venue,
                        'organizer': manager,
                        'event_manager': manager,
                        'status': 'confirmed',
                        'payment_status': 'paid',
                        'total_budget': event_data['total_budget'],
                        'venue_cost': event_data['venue_cost'],
                        'vendor_costs': event_data['vendor_costs'],
                        'manager_fee': event_data['manager_fee'],
                        'total_cost': event_data['total_cost'],
                        'theme': event_data['theme'],
                        'special_requirements': event_data['special_requirements'],
                        'tags': event_data['tags']
                    }
                )
                
                if created:
                    self.stdout.write(f'Created event: {event.title}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created real events from Gandhinagar and Ahmedabad!')
        ) 