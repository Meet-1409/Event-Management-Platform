#!/bin/bash

# 360° Event Manager - Development Bootstrap Script
# This script sets up the development environment and runs the application

set -e  # Exit on any error

echo "🚀 360° Event Manager - Development Setup"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate

# Install requirements
echo "📚 Installing requirements..."
pip install -r requirements.txt

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p logs

# Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput || echo "⚠️  Static files collection failed (non-critical)"

# Run migrations
echo "🗄️  Running database migrations..."
python manage.py migrate

# Check if superuser exists, create if not
echo "👤 Setting up admin user..."
python manage.py shell -c "
from users.models import CustomUser
if not CustomUser.objects.filter(email='admin@example.com').exists():
    admin = CustomUser.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123',
        first_name='Admin',
        last_name='User',
        user_type='admin'
    )
    print('✅ Superuser created: admin@example.com / adminpass123')
else:
    print('✅ Superuser already exists: admin@example.com')
"

# Seed minimal data
echo "🌱 Seeding minimal data..."
python manage.py shell -c "
from users.models import CustomUser
from venues.models import Venue, VenueCategory
from events.models import Event, EventType, Registration
from payments.models import Payment, PaymentMethod, Invoice
from decimal import Decimal
from datetime import date, time

print('Creating basic data...')

# Create venue category and venue
venue_cat, _ = VenueCategory.objects.get_or_create(
    name='Conference Hall',
    defaults={'description': 'Professional conference venues'}
)

venue, _ = Venue.objects.get_or_create(
    name='Grand Conference Center',
    defaults={
        'category': venue_cat,
        'address': '123 Business District, Ahmedabad',
        'city': 'Ahmedabad',
        'state': 'Gujarat',
        'country': 'IN',
        'capacity_min': 50,
        'capacity_max': 500,
        'base_price': Decimal('8000.00'),
        'description': 'Modern conference center with state-of-the-art facilities',
        'status': 'active'
    }
)

# Create event type and event
event_type, _ = EventType.objects.get_or_create(
    name='Corporate',
    defaults={'description': 'Corporate events and conferences'}
)

# Create test manager
manager, _ = CustomUser.objects.get_or_create(
    username='manager1',
    defaults={
        'email': 'manager@example.com',
        'first_name': 'Event',
        'last_name': 'Manager',
        'user_type': 'manager',
        'phone_number': '+919876543210'
    }
)
manager.set_password('managerpass123')
manager.save()

# Create test user
user, _ = CustomUser.objects.get_or_create(
    username='testuser',
    defaults={
        'email': 'user@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'user_type': 'user',
        'phone_number': '+919876543211'
    }
)
user.set_password('userpass123')
user.save()

# Create test event
event, _ = Event.objects.get_or_create(
    title='Tech Conference 2024',
    defaults={
        'description': 'Annual technology conference with industry leaders',
        'event_type': event_type,
        'start_date': date(2024, 12, 15),
        'end_date': date(2024, 12, 15),
        'start_time': time(9, 0),
        'end_time': time(17, 0),
        'expected_guests': 200,
        'venue': venue,
        'organizer': manager,
        'total_budget': Decimal('50000.00'),
        'venue_cost': Decimal('15000.00'),
        'total_cost': Decimal('50000.00'),
        'status': 'confirmed',
        'is_public': True
    }
)

# Create payment method
payment_method, _ = PaymentMethod.objects.get_or_create(
    name='dev_mode',
    defaults={
        'payment_type': 'credit_card',
        'is_active': True,
        'processing_fee_percentage': Decimal('2.5')
    }
)

print('✅ Basic data seeded successfully')
print(f'✅ Venue: {venue.name}')
print(f'✅ Event: {event.title}')
print(f'✅ Manager: {manager.email} / managerpass123')
print(f'✅ User: {user.email} / userpass123')
"

echo ""
echo "✅ Development setup completed successfully!"
echo ""
echo "🔑 Login Credentials:"
echo "   Admin:   admin@example.com / adminpass123"
echo "   Manager: manager@example.com / managerpass123"  
echo "   User:    user@example.com / userpass123"
echo ""
echo "🌐 Starting development server..."
echo "   Access at: http://127.0.0.1:8000"
echo ""

# Start the development server
python manage.py runserver 0.0.0.0:8000
