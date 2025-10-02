from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from events.models import Event, EventType
from venues.models import Venue, VenueCategory
from users.models import CustomUser
from decimal import Decimal
from datetime import date, time, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed the gallery with more sample events'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample events for gallery...')
        
        # Get or create event types
        event_types = {
            'Corporate': EventType.objects.get_or_create(name='Corporate', defaults={'description': 'Corporate events and conferences'})[0],
            'Wedding': EventType.objects.get_or_create(name='Wedding', defaults={'description': 'Wedding ceremonies and receptions'})[0],
            'Birthday': EventType.objects.get_or_create(name='Birthday', defaults={'description': 'Birthday parties and celebrations'})[0],
            'Sports': EventType.objects.get_or_create(name='Sports', defaults={'description': 'Sports events and tournaments'})[0],
            'Music': EventType.objects.get_or_create(name='Music', defaults={'description': 'Music concerts and performances'})[0],
            'Cultural': EventType.objects.get_or_create(name='Cultural', defaults={'description': 'Cultural events and festivals'})[0],
        }
        
        # Get or create venue category
        venue_cat, _ = VenueCategory.objects.get_or_create(
            name='Multi-Purpose Hall',
            defaults={'description': 'Versatile venues for various events'}
        )
        
        # Get or create venues
        venues = []
        venue_data = [
            {
                'name': 'Grand Conference Center',
                'address': '123 Business District, Ahmedabad',
                'city': 'Ahmedabad',
                'state': 'Gujarat',
                'capacity_min': 50,
                'capacity_max': 500,
                'base_price': Decimal('8000.00'),
                'description': 'Modern conference center with state-of-the-art facilities'
            },
            {
                'name': 'Royal Wedding Palace',
                'address': '456 Heritage Road, Gandhinagar',
                'city': 'Gandhinagar',
                'state': 'Gujarat',
                'capacity_min': 100,
                'capacity_max': 800,
                'base_price': Decimal('15000.00'),
                'description': 'Elegant wedding venue with traditional and modern amenities'
            },
            {
                'name': 'Sports Complex Arena',
                'address': '789 Sports Avenue, Ahmedabad',
                'city': 'Ahmedabad',
                'state': 'Gujarat',
                'capacity_min': 200,
                'capacity_max': 1000,
                'base_price': Decimal('12000.00'),
                'description': 'Professional sports facility with modern equipment'
            },
            {
                'name': 'Cultural Center Hall',
                'address': '321 Art District, Gandhinagar',
                'city': 'Gandhinagar',
                'state': 'Gujarat',
                'capacity_min': 80,
                'capacity_max': 400,
                'base_price': Decimal('10000.00'),
                'description': 'Cultural venue perfect for performances and exhibitions'
            },
            {
                'name': 'Garden Party Venue',
                'address': '654 Green Park, Ahmedabad',
                'city': 'Ahmedabad',
                'state': 'Gujarat',
                'capacity_min': 50,
                'capacity_max': 300,
                'base_price': Decimal('7000.00'),
                'description': 'Beautiful outdoor venue with garden setting'
            }
        ]
        
        for venue_info in venue_data:
            venue, _ = Venue.objects.get_or_create(
                name=venue_info['name'],
                defaults={
                    'category': venue_cat,
                    'address': venue_info['address'],
                    'city': venue_info['city'],
                    'state': venue_info['state'],
                    'country': 'IN',
                    'capacity_min': venue_info['capacity_min'],
                    'capacity_max': venue_info['capacity_max'],
                    'base_price': venue_info['base_price'],
                    'description': venue_info['description'],
                    'status': 'active'
                }
            )
            venues.append(venue)
        
        # Get or create event managers
        managers = []
        manager_data = [
            {
                'username': 'manager1',
                'email': 'manager@example.com',
                'first_name': 'Event',
                'last_name': 'Manager',
                'user_type': 'manager',
                'phone_number': '+919876543210'
            },
            {
                'username': 'manager2',
                'email': 'manager2@example.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'user_type': 'manager',
                'phone_number': '+919876543211'
            },
            {
                'username': 'manager3',
                'email': 'manager3@example.com',
                'first_name': 'Raj',
                'last_name': 'Patel',
                'user_type': 'manager',
                'phone_number': '+919876543212'
            }
        ]
        
        for manager_info in manager_data:
            manager, _ = CustomUser.objects.get_or_create(
                username=manager_info['username'],
                defaults=manager_info
            )
            manager.set_password('managerpass123')
            manager.save()
            managers.append(manager)
        
        # Sample events data
        events_data = [
            {
                'title': 'Annual Football Championship 2024',
                'description': 'Successfully organized football tournament with 32 teams and 500+ spectators. The event featured professional referees, live commentary, and exciting matches that kept the audience engaged throughout the day.',
                'event_type': 'Sports',
                'venue': 'Sports Complex Arena',
                'manager': 'manager1',
                'start_date': date(2024, 6, 15),
                'end_date': date(2024, 6, 15),
                'start_time': time(9, 0),
                'end_time': time(18, 0),
                'expected_guests': 500,
                'actual_guests': 480,
                'total_budget': Decimal('75000.00'),
                'venue_cost': Decimal('12000.00'),
                'total_cost': Decimal('75000.00'),
                'rating': 3.8,
                'reviews': 6
            },
            {
                'title': 'Tech Innovation Summit 2024',
                'description': 'A comprehensive technology conference featuring industry leaders, innovative startups, and cutting-edge presentations. The event included keynote speeches, panel discussions, and networking sessions.',
                'event_type': 'Corporate',
                'venue': 'Grand Conference Center',
                'manager': 'manager2',
                'start_date': date(2024, 7, 20),
                'end_date': date(2024, 7, 21),
                'start_time': time(9, 0),
                'end_time': time(17, 0),
                'expected_guests': 300,
                'actual_guests': 285,
                'total_budget': Decimal('120000.00'),
                'venue_cost': Decimal('16000.00'),
                'total_cost': Decimal('120000.00'),
                'rating': 4.5,
                'reviews': 12
            },
            {
                'title': 'Royal Wedding Celebration',
                'description': 'A magnificent wedding celebration with traditional Gujarati rituals and modern entertainment. The event featured live music, traditional dance performances, and exquisite cuisine.',
                'event_type': 'Wedding',
                'venue': 'Royal Wedding Palace',
                'manager': 'manager3',
                'start_date': date(2024, 8, 10),
                'end_date': date(2024, 8, 10),
                'start_time': time(16, 0),
                'end_time': time(23, 0),
                'expected_guests': 400,
                'actual_guests': 420,
                'total_budget': Decimal('200000.00'),
                'venue_cost': Decimal('30000.00'),
                'total_cost': Decimal('200000.00'),
                'rating': 4.8,
                'reviews': 8
            },
            {
                'title': 'Cultural Heritage Festival',
                'description': 'A vibrant celebration of local culture featuring traditional music, dance performances, art exhibitions, and local cuisine. The festival attracted visitors from across the state.',
                'event_type': 'Cultural',
                'venue': 'Cultural Center Hall',
                'manager': 'manager1',
                'start_date': date(2024, 9, 5),
                'end_date': date(2024, 9, 7),
                'start_time': time(10, 0),
                'end_time': time(22, 0),
                'expected_guests': 600,
                'actual_guests': 650,
                'total_budget': Decimal('85000.00'),
                'venue_cost': Decimal('20000.00'),
                'total_cost': Decimal('85000.00'),
                'rating': 4.2,
                'reviews': 15
            },
            {
                'title': 'Birthday Bash Extravaganza',
                'description': 'A spectacular birthday celebration with themed decorations, live entertainment, and gourmet catering. The event featured a photo booth, games, and surprise performances.',
                'event_type': 'Birthday',
                'venue': 'Garden Party Venue',
                'manager': 'manager2',
                'start_date': date(2024, 10, 12),
                'end_date': date(2024, 10, 12),
                'start_time': time(18, 0),
                'end_time': time(23, 0),
                'expected_guests': 150,
                'actual_guests': 160,
                'total_budget': Decimal('45000.00'),
                'venue_cost': Decimal('7000.00'),
                'total_cost': Decimal('45000.00'),
                'rating': 4.6,
                'reviews': 9
            },
            {
                'title': 'Music Concert Under the Stars',
                'description': 'An unforgettable outdoor music concert featuring local and national artists. The event included professional sound and lighting, food stalls, and a magical atmosphere.',
                'event_type': 'Music',
                'venue': 'Garden Party Venue',
                'manager': 'manager3',
                'start_date': date(2024, 11, 8),
                'end_date': date(2024, 11, 8),
                'start_time': time(19, 0),
                'end_time': time(23, 0),
                'expected_guests': 250,
                'actual_guests': 280,
                'total_budget': Decimal('65000.00'),
                'venue_cost': Decimal('14000.00'),
                'total_cost': Decimal('65000.00'),
                'rating': 4.4,
                'reviews': 11
            },
            {
                'title': 'Corporate Annual Meeting',
                'description': 'A professional corporate gathering with presentations, team building activities, and award ceremonies. The event featured modern AV equipment and professional catering.',
                'event_type': 'Corporate',
                'venue': 'Grand Conference Center',
                'manager': 'manager1',
                'start_date': date(2024, 12, 3),
                'end_date': date(2024, 12, 3),
                'start_time': time(9, 0),
                'end_time': time(17, 0),
                'expected_guests': 200,
                'actual_guests': 195,
                'total_budget': Decimal('55000.00'),
                'venue_cost': Decimal('8000.00'),
                'total_cost': Decimal('55000.00'),
                'rating': 4.1,
                'reviews': 7
            },
            {
                'title': 'Sports Day Championship',
                'description': 'A comprehensive sports day event featuring multiple sports competitions, awards ceremony, and entertainment. The event promoted healthy competition and team spirit.',
                'event_type': 'Sports',
                'venue': 'Sports Complex Arena',
                'manager': 'manager2',
                'start_date': date(2024, 5, 25),
                'end_date': date(2024, 5, 25),
                'start_time': time(8, 0),
                'end_time': time(19, 0),
                'expected_guests': 350,
                'actual_guests': 380,
                'total_budget': Decimal('60000.00'),
                'venue_cost': Decimal('12000.00'),
                'total_cost': Decimal('60000.00'),
                'rating': 4.3,
                'reviews': 13
            }
        ]
        
        # Create events
        created_count = 0
        for event_data in events_data:
            # Find venue and manager
            venue = next((v for v in venues if v.name == event_data['venue']), venues[0])
            manager = next((m for m in managers if m.username == event_data['manager']), managers[0])
            event_type = event_types[event_data['event_type']]
            
            event, created = Event.objects.get_or_create(
                title=event_data['title'],
                defaults={
                    'description': event_data['description'],
                    'event_type': event_type,
                    'start_date': event_data['start_date'],
                    'end_date': event_data['end_date'],
                    'start_time': event_data['start_time'],
                    'end_time': event_data['end_time'],
                    'expected_guests': event_data['expected_guests'],
                    'actual_guests': event_data['actual_guests'],
                    'venue': venue,
                    'organizer': manager,
                    'total_budget': event_data['total_budget'],
                    'venue_cost': event_data['venue_cost'],
                    'total_cost': event_data['total_cost'],
                    'status': 'completed',
                    'is_public': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'Created event: {event.title}')
                
                # Create sample reviews for the event
                self.create_sample_reviews(event, event_data['rating'], event_data['reviews'])
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} new events for the gallery!')
        )
    
    def create_sample_reviews(self, event, avg_rating, review_count):
        """Create sample reviews for an event"""
        from events.models import EventReview
        
        # Sample review data
        review_data = [
            {'title': 'Amazing Event!', 'comment': 'This was one of the best events I have ever attended. Everything was perfectly organized and the atmosphere was incredible.'},
            {'title': 'Great Experience', 'comment': 'The event exceeded my expectations. The organizers did a fantastic job and I would definitely attend again.'},
            {'title': 'Well Organized', 'comment': 'Professional event management with attention to detail. The venue was perfect and the staff was very helpful.'},
            {'title': 'Memorable Day', 'comment': 'A truly memorable experience. The event was well-planned and executed flawlessly. Highly recommended!'},
            {'title': 'Outstanding Service', 'comment': 'The team went above and beyond to ensure everyone had a great time. The quality of service was exceptional.'},
            {'title': 'Perfect Venue', 'comment': 'The venue was beautiful and perfectly suited for this type of event. The facilities were top-notch.'},
            {'title': 'Excellent Value', 'comment': 'Great value for money. The event was well worth the cost and provided excellent entertainment.'},
            {'title': 'Highly Recommended', 'comment': 'I would highly recommend this event to anyone. The organizers are professional and the experience is unforgettable.'},
            {'title': 'Fantastic Atmosphere', 'comment': 'The atmosphere was electric and everyone had a great time. The event was perfectly timed and executed.'},
            {'title': 'Top Quality Event', 'comment': 'This was a top-quality event with professional organization and excellent attention to detail.'},
        ]
        
        # Create users for reviews if they don't exist
        review_users = []
        for i in range(review_count):
            user, _ = CustomUser.objects.get_or_create(
                username=f'reviewer_{event.id}_{i}',
                defaults={
                    'email': f'reviewer_{event.id}_{i}@example.com',
                    'first_name': f'Reviewer',
                    'last_name': f'{i+1}',
                    'user_type': 'user',
                    'phone_number': f'+9198765432{i:02d}'
                }
            )
            user.set_password('userpass123')
            user.save()
            review_users.append(user)
        
        # Create reviews with ratings that average to the target
        ratings = self.generate_ratings(avg_rating, review_count)
        
        for i, (user, rating) in enumerate(zip(review_users, ratings)):
            review_info = review_data[i % len(review_data)]
            EventReview.objects.create(
                event=event,
                user=user,
                rating=rating,
                title=review_info['title'],
                comment=review_info['comment'],
                is_approved=True
            )
    
    def generate_ratings(self, target_avg, count):
        """Generate ratings that average to the target"""
        import random
        
        # Generate ratings that will average close to target_avg
        ratings = []
        remaining_sum = target_avg * count
        
        for i in range(count - 1):
            # Calculate min and max possible ratings for remaining slots
            min_rating = max(1, remaining_sum - (count - i - 1) * 5)
            max_rating = min(5, remaining_sum - (count - i - 1) * 1)
            
            # Add some randomness
            if min_rating == max_rating:
                rating = min_rating
            else:
                rating = random.randint(int(min_rating), int(max_rating))
            
            ratings.append(rating)
            remaining_sum -= rating
        
        # Last rating
        ratings.append(max(1, min(5, int(remaining_sum))))
        
        # Shuffle to make it more realistic
        random.shuffle(ratings)
        return ratings
