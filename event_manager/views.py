from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import TemplateView
from users import role_required
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from events.models import Event
from venues.models import Venue
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)

def home_view(request):
    """Home page - accessible to everyone"""
    return render(request, 'event_manager/home.html')

def about_view(request):
    """About page - accessible to everyone"""
    return render(request, 'about.html')

def contact_view(request):
    """Contact page - accessible to everyone"""
    return render(request, 'contact.html')

def privacy_view(request):
    """Privacy page - accessible to everyone"""
    return render(request, 'privacy.html')

def terms_view(request):
    """Terms page - accessible to everyone"""
    return render(request, 'terms.html')

def cookie_policy_view(request):
    """Cookie Policy page - accessible to everyone"""
    return render(request, 'cookie_policy.html')

def gdpr_view(request):
    """GDPR Compliance page - accessible to everyone"""
    return render(request, 'gdpr.html')

def help_center_view(request):
    """Help Center page - accessible to everyone"""
    return render(request, 'help_center.html')

def support_view(request):
    """Support page - accessible to everyone"""
    return render(request, 'support.html')

def gallery_view(request):
    """Event gallery page - accessible to everyone"""
    from events.models import Event, EventReview
    from django.db.models import Avg
    
    try:
        # Get COMPLETED events to showcase previous work (with or without photos)
        events = Event.objects.filter(
            is_public=True,
            status='completed'  # Only completed events
        ).order_by('-created_at')
        
        # Add rating information for each event
        for event in events:
            try:
                reviews = event.reviews.filter(is_approved=True)
                event.avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
                event.total_reviews = reviews.count()
                # Add success metrics
                event.guest_satisfaction = round(event.avg_rating * 20, 1) if event.avg_rating > 0 else 0  # Convert to percentage
            except Exception as e:
                # Handle any errors with individual events
                event.avg_rating = 0
                event.total_reviews = 0
                event.guest_satisfaction = 0
                logger.error(f"Error processing event {event.id}: {e}")
        
        # Get statistics for the gallery
        total_completed = Event.objects.filter(status='completed').count()
        total_guests_served = sum(event.actual_guests or event.expected_guests for event in Event.objects.filter(status='completed'))
        avg_satisfaction = events.aggregate(Avg('reviews__rating'))['reviews__rating__avg'] or 0
        
        context = {
            'events': events,
            'title': 'Event Gallery - Our Success Stories',
            'subtitle': 'Showcasing our successfully completed events and satisfied customers',
            'stats': {
                'total_events': total_completed,
                'total_guests': total_guests_served,
                'satisfaction_rate': round(avg_satisfaction * 20, 1) if avg_satisfaction > 0 else 95,  # Convert to percentage
                'gallery_events': events.count()
            }
        }
        return render(request, 'gallery.html', context)
        
    except Exception as e:
        # Handle any database errors
        logger.error(f"Gallery view error: {e}")
        context = {
            'events': [],
            'title': 'Event Gallery',
            'subtitle': 'Explore our successful events and get inspired for your next celebration',
            'error': 'Unable to load events at this time. Please try again later.'
        }
        return render(request, 'gallery.html', context)

def testimonials_view(request):
    """Testimonials page - accessible to everyone"""
    return render(request, 'testimonials.html')

def pricing_view(request):
    """Pricing page - accessible to everyone"""
    return render(request, 'pricing.html')

def faq_view(request):
    """FAQ page - accessible to everyone"""
    return render(request, 'faq.html')

def ai_mood_designer_view(request):
    """AI Mood Designer page - accessible to everyone"""
    return render(request, 'ai_mood_designer.html')

@csrf_exempt
@require_POST
def ai_chatbot_process(request):
    """Process AI chatbot messages with real-time data"""
    if request.method == 'POST':
        import json
        from django.http import JsonResponse
        from events.models import Event
        from venues.models import Venue
        from django.db.models import Q
        
        data = json.loads(request.body)
        message = data.get('message', '').lower()
        
        # Real-time data fetching with error handling
        try:
            upcoming_events = Event.objects.filter(
                start_date__gte=timezone.now().date(),
                status__in=['confirmed', 'completed']
            ).order_by('start_date')[:5]
            
            available_venues = Venue.objects.filter(
                status='active'
            ).order_by('name')[:5]
            
            # Smart response generation based on user query
            if any(word in message for word in ['event', 'events', 'upcoming', 'tomorrow', 'today']):
                if upcoming_events.exists():
                    response = "Here are the upcoming events:\n\n"
                    for event in upcoming_events:
                        response += f"🎯 {event.title}\n"
                        response += f"📅 {event.start_date.strftime('%B %d, %Y')}\n"
                        response += f"📍 {event.venue.name}\n"
                        response += f"💰 ₹{event.total_cost}\n\n"
                    response += "Would you like to book any of these events?"
                else:
                    response = "Currently, there are no upcoming events. Would you like to check our venue availability or contact us for custom event planning?"
            
            elif any(word in message for word in ['venue', 'venues', 'location', 'place']):
                if available_venues.exists():
                    response = "Here are our available venues:\n\n"
                    for venue in available_venues:
                        response += f"🏢 {venue.name}\n"
                        response += f"📍 {venue.address}\n"
                        response += f"💰 Starting from ₹{venue.price_per_hour}/hour\n"
                        response += f"👥 Capacity: {venue.capacity} people\n\n"
                    response += "Would you like to book a venue or see more details?"
                else:
                    response = "Currently, all venues are booked. Please contact us for availability or alternative options."
            
            elif any(word in message for word in ['book', 'booking', 'reserve', 'reservation']):
                response = "Great! To book an event or venue:\n\n"
                response += "1️⃣ Browse events at: /events/\n"
                response += "2️⃣ Check venues at: /venues/\n"
                response += "3️⃣ Contact us at: /contact/\n"
                response += "4️⃣ Call us: +91 98765 43210\n\n"
                response += "Would you like me to help you with a specific booking?"
            
            elif any(word in message for word in ['price', 'cost', 'fee', 'payment']):
                response = "Our pricing structure:\n\n"
                response += "🎪 Event Planning: ₹5,000 - ₹50,000\n"
                response += "🏢 Venue Rental: ₹2,000 - ₹25,000/hour\n"
                response += "🎵 Entertainment: ₹3,000 - ₹30,000\n"
                response += "🍽️ Catering: ₹500 - ₹2,000/person\n\n"
                response += "We accept Paytm, UPI, and card payments. Would you like a detailed quote?"
            
            elif any(word in message for word in ['contact', 'help', 'support']):
                response = "Here's how to reach us:\n\n"
                response += "📞 Phone: +91 98765 43210\n"
                response += "📧 Email: info@360eventmanager.com\n"
                response += "📍 Address: Ahmedabad, Gujarat\n"
                response += "🌐 Website: /contact/\n\n"
                response += "We're available 24/7 for your event planning needs!"
            
            elif any(word in message for word in ['football', 'sport', 'tournament']):
                response = "⚽ Football Tournament Details:\n\n"
                response += "🏟️ Venue: Sports Complex, Ahmedabad\n"
                response += "📅 Date: Check our events page\n"
                response += "💰 Entry Fee: ₹1,000 per team\n"
                response += "🏆 Prize Pool: ₹50,000\n\n"
                response += "Register now at: /events/"
            
            elif any(word in message for word in ['hello', 'hi', 'hey', 'help']):
                response = "Hello! 👋 Welcome to 360° Event Manager!\n\n"
                response += "I'm your personal event assistant. I can help you with:\n\n"
                response += "🎯 Finding and booking events\n"
                response += "🏢 Discovering perfect venues\n"
                response += "💰 Getting pricing information\n"
                response += "📞 Connecting with event managers\n"
                response += "🎵 Event planning tips and advice\n\n"
                response += "What can I help you with today? Try asking about events, venues, or pricing!"
            
            elif any(word in message for word in ['error', 'problem', 'issue', 'not working']):
                response = "I'm sorry you're experiencing an issue! 😔\n\n"
                response += "Here's how I can help:\n\n"
                response += "🔧 Try refreshing the page\n"
                response += "📞 Contact our support: +91 98765 43210\n"
                response += "📧 Email us: info@360eventmanager.com\n"
                response += "💬 Use the chat system to talk to our team\n\n"
                response += "Is there something specific I can help you find?"
            
            else:
                response = "I'm your 360° Event Assistant! 🎉\n\n"
                response += "I can help you with:\n\n"
                response += "🎯 Event booking and planning\n"
                response += "🏢 Venue selection and rental\n"
                response += "💰 Pricing and payment options\n"
                response += "📞 Contact and support\n"
                response += "🎵 Event management tips\n\n"
                response += "Try asking me about:\n"
                response += "• 'Show me events'\n"
                response += "• 'Find venues in Ahmedabad'\n"
                response += "• 'What are your prices?'\n"
                response += "• 'How to book an event?'"
            
            return JsonResponse({
                'success': True,
                'response': response,
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'response': 'Sorry, I encountered an error. Please try again or contact our support team.',
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'response': 'Invalid request method'})

def generate_ai_response(message, events, venues):
    """Generate AI response based on user message and real data"""
    
    # Check for event-related queries
    if any(word in message for word in ['event', 'events', 'upcoming', 'available', 'happening']):
        if events.exists():
            event_list = []
            for event in events:
                event_list.append(f"🎪 **{event.title}** - {event.start_date.strftime('%B %d, %Y')}\n📍 {event.location}\n💰 ₹{event.total_cost:,}")
            
            response_text = f"Here are some exciting upcoming events:\n\n" + "\n\n".join(event_list)
            response_text += "\n\nWould you like me to show you more details about any of these events?"
        else:
            response_text = "I can show you our events page where you can see all upcoming events and book them directly. Would you like me to do that?"
        
        return {
            'message': response_text,
            'action': 'show_events_list',
            'action_data': {
                'events_count': events.count(),
                'events': list(events.values('title', 'start_date', 'location', 'total_cost'))
            }
        }
    
    # Check for venue-related queries
    elif any(word in message for word in ['venue', 'venues', 'location', 'place', 'where']):
        if venues.exists():
            venue_list = []
            for venue in venues:
                venue_list.append(f"🏢 **{venue.name}**\n📍 {venue.address}\n💰 Starting from ₹{venue.base_price:,}")
            
            response_text = f"Here are some popular venues in your area:\n\n" + "\n\n".join(venue_list)
            response_text += "\n\nWould you like me to show you more venues or help you book one?"
        else:
            response_text = "I can show you our venues page with detailed information, photos, and availability. Would you like to see that?"
        
        return {
            'message': response_text,
            'action': 'show_venues_list',
            'action_data': {
                'venues_count': venues.count(),
                'venues': list(venues.values('name', 'address', 'base_price'))
            }
        }
    
    # Check for booking-related queries
    elif any(word in message for word in ['book', 'booking', 'register', 'registration', 'how to']):
        response_text = """Booking an event is super easy! Here's the step-by-step process:

1️⃣ **Browse Events** - Visit our events page
2️⃣ **Select Event** - Choose your preferred event
3️⃣ **Fill Details** - Provide your information
4️⃣ **Make Payment** - Secure online payment
5️⃣ **Confirmation** - Receive booking confirmation

I can help you with any specific step. What would you like to know?"""
        
        return {
            'message': response_text,
            'action': 'show_booking_guide'
        }
    
    # Check for pricing-related queries
    elif any(word in message for word in ['price', 'cost', 'fee', 'payment', 'money', 'budget']):
        if events.exists():
            min_price = min(event.total_cost for event in events)
            max_price = max(event.total_cost for event in events)
            response_text = f"""Our pricing varies based on event type and venue:

💰 **Current Event Prices**: ₹{min_price:,} - ₹{max_price:,}

We also offer special discounts for:
• Early bookings (10% off)
• Group bookings (15% off)
• Corporate clients (20% off)

Would you like me to help you find the best option for your budget?"""
        else:
            response_text = """Our pricing varies based on event type and venue:

💰 **Basic Events** - Starting from ₹5,000
💰 **Standard Events** - Starting from ₹15,000
💰 **Premium Events** - Starting from ₹50,000
💰 **Luxury Events** - Starting from ₹1,00,000

Would you like me to help you find the best option for your budget?"""
        
        return {
            'message': response_text,
            'action': 'show_pricing',
            'action_data': {
                'min_price': min_price if events.exists() else 5000,
                'max_price': max_price if events.exists() else 100000
            }
        }
    
    # Default response
    else:
        response_text = """I'm your 360° Event Assistant! I can help you with:

• Finding and booking events
• Discovering venues
• Getting pricing information
• Event planning tips
• Customer support

Just let me know what you need help with!"""
        
        return {
            'message': response_text,
            'action': 'general_help'
        }

def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500) 