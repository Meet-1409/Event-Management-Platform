from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from events.models import Event, Registration
from users.models import CustomUser
from decimal import Decimal
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Create sample bookings with Indian names'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample bookings with Indian names...')
        
        with transaction.atomic():
            # Indian names for sample bookings
            indian_names = [
                'Rajesh Patel', 'Priya Sharma', 'Amit Shah', 'Kavita Desai', 'Vikram Mehta',
                'Sunita Iyer', 'Rahul Singh', 'Meera Patel', 'Arjun Verma', 'Anjali Gupta',
                'Deepak Kumar', 'Pooja Sharma', 'Suresh Reddy', 'Kiran Patel', 'Mohan Das',
                'Lakshmi Devi', 'Ramesh Kumar', 'Geeta Singh', 'Prakash Patel', 'Rekha Sharma',
                'Naresh Gupta', 'Sita Patel', 'Harish Mehta', 'Uma Devi', 'Sanjay Kumar',
                'Anita Patel', 'Rajiv Singh', 'Maya Sharma', 'Dinesh Patel', 'Rashmi Gupta',
                'Mukesh Kumar', 'Jyoti Patel', 'Vijay Singh', 'Neha Sharma', 'Girish Patel',
                'Shweta Gupta', 'Rakesh Kumar', 'Pallavi Patel', 'Sandeep Singh', 'Divya Sharma',
                'Harsh Patel', 'Kirti Gupta', 'Nitin Kumar', 'Ritu Patel', 'Amit Singh',
                'Priyanka Sharma', 'Ravi Patel', 'Monika Gupta', 'Ajay Kumar', 'Sneha Patel',
                'Vivek Singh', 'Ruchi Sharma', 'Pankaj Patel', 'Ankita Gupta', 'Rohit Kumar',
                'Tanvi Patel', 'Abhishek Singh', 'Shivani Sharma', 'Gaurav Patel', 'Nisha Gupta',
                'Manish Kumar', 'Pooja Patel', 'Rahul Singh', 'Kavya Sharma', 'Amit Patel',
                'Riya Gupta', 'Vikrant Kumar', 'Anjali Patel', 'Saurabh Singh', 'Isha Sharma',
                'Ritesh Patel', 'Neha Gupta', 'Aditya Kumar', 'Priya Patel', 'Rohan Singh',
                'Zara Sharma', 'Kunal Patel', 'Aisha Gupta', 'Arnav Kumar', 'Diya Patel',
                'Shaurya Singh', 'Myra Sharma', 'Vivaan Patel', 'Aarav Gupta', 'Advait Kumar',
                'Aaradhya Patel', 'Vihaan Singh', 'Ananya Sharma', 'Krish Patel', 'Aisha Gupta',
                'Arjun Kumar', 'Zara Patel', 'Shaurya Singh', 'Myra Sharma', 'Vivaan Patel',
                'Aarav Gupta', 'Advait Kumar', 'Aaradhya Patel', 'Vihaan Singh', 'Ananya Sharma'
            ]
            
            # Get public events
            public_events = Event.objects.filter(is_public=True, status='confirmed')
            
            if not public_events.exists():
                self.stdout.write('No public events found. Please run create_real_events first.')
                return
            
            # Create sample bookings for the past 6 months
            base_date = date.today()
            bookings_created = 0
            
            for i in range(100):  # Create 100 sample bookings
                # Random event
                event = random.choice(public_events)
                
                # Random date in the past 6 months
                days_ago = random.randint(1, 180)
                booking_date = base_date - timedelta(days=days_ago)
                
                # Random name
                name = random.choice(indian_names)
                
                # Generate email from name
                name_parts = name.lower().split()
                email = f"{name_parts[0]}.{name_parts[1]}@gmail.com"
                
                # Generate phone number
                phone = f"+91-{random.randint(7000000000, 9999999999)}"
                
                # Check if registration already exists
                if not Registration.objects.filter(event=event, email=email).exists():
                    registration = Registration.objects.create(
                        event=event,
                        name=name,
                        email=email,
                        phone=phone,
                        created_at=timezone.now() - timedelta(days=days_ago)
                    )
                    bookings_created += 1
                    
                    if bookings_created % 10 == 0:
                        self.stdout.write(f'Created {bookings_created} bookings...')
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {bookings_created} sample bookings with Indian names!')
            ) 