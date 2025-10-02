from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from io import BytesIO
import os
from datetime import datetime
import random
from datetime import datetime, timedelta
from django.db.models import Q, Count, Avg
from django.contrib.auth import get_user_model
from .models import Event, EventType, Registration
from users.models import UserProfile

User = get_user_model()

def generate_pdf_invoice(event, user):
    """Generate PDF invoice for event booking"""
    
    # Prepare context data
    context = {
        'event': event,
        'user': user,
        'invoice_number': f"INV-{event.id:06d}",
        'invoice_date': datetime.now().strftime("%B %d, %Y"),
        'due_date': (datetime.now().replace(day=datetime.now().day + 30)).strftime("%B %d, %Y"),
        'company_info': {
            'name': '360° Event Manager',
            'address': 'Ahmedabad, Gujarat, India',
            'phone': '+91 98765 43210',
            'email': 'info@360eventmanager.com',
            'website': 'www.360eventmanager.com'
        }
    }
    
    # Load template
    template = get_template('events/invoice_template.html')
    html = template.render(context)
    
    # Create PDF
    result = BytesIO()
    pdf = pisa.CreatePDF(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    
    return None

def generate_event_report(event):
    """Generate PDF report for event details"""
    
    context = {
        'event': event,
        'report_date': datetime.now().strftime("%B %d, %Y"),
        'company_info': {
            'name': '360° Event Manager',
            'address': 'Ahmedabad, Gujarat, India',
            'phone': '+91 98765 43210',
            'email': 'info@360eventmanager.com'
        }
    }
    
    template = get_template('events/event_report_template.html')
    html = template.render(context)
    
    result = BytesIO()
    pdf = pisa.CreatePDF(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    
    return None 

def generate_event_id():
    """Generate a unique event ID"""
    import uuid
    return f"EVT{uuid.uuid4().hex[:8].upper()}"

def calculate_event_rating(event):
    """Calculate average rating for an event"""
    reviews = event.reviews.all()
    if reviews.exists():
        return reviews.aggregate(Avg('rating'))['rating__avg']
    return 0

def get_popular_events(limit=6):
    """Get popular events based on registrations and ratings"""
    events = Event.objects.filter(
        status='confirmed',
        start_date__gte=datetime.now().date()
    ).annotate(
        registration_count=Count('registrations'),
        avg_rating=Avg('reviews__rating')
    ).order_by('-registration_count', '-avg_rating')[:limit]
    
    return events

def get_recommended_events_for_user(user, limit=6):
    """AI-powered event recommendations based on user preferences and behavior"""
    if not user.is_authenticated:
        return get_popular_events(limit)
    
    try:
        user_profile = user.user_profile
    except UserProfile.DoesNotExist:
        return get_popular_events(limit)
    
    # Get user preferences
    preferred_types = user_profile.preferred_event_types or []
    preferred_venues = user_profile.preferred_venues or []
    budget_range = user_profile.budget_range
    
    # Build recommendation query
    query = Q(status='confirmed', start_date__gte=datetime.now().date())
    
    # Filter by preferred event types
    if preferred_types:
        query &= Q(event_type__name__in=preferred_types)
    
    # Filter by budget range
    if budget_range:
        if budget_range == 'low':
            query &= Q(total_cost__lte=5000)
        elif budget_range == 'medium':
            query &= Q(total_cost__gt=5000, total_cost__lte=20000)
        elif budget_range == 'high':
            query &= Q(total_cost__gt=20000)
    
    # Get events matching preferences
    recommended_events = Event.objects.filter(query).annotate(
        registration_count=Count('registrations'),
        avg_rating=Avg('reviews__rating')
    ).order_by('-avg_rating', '-registration_count')[:limit]
    
    # If not enough events, add popular events
    if recommended_events.count() < limit:
        remaining_limit = limit - recommended_events.count()
        popular_events = get_popular_events(remaining_limit)
        recommended_events = list(recommended_events) + list(popular_events)
    
    return recommended_events[:limit]

def get_similar_events(event, limit=4):
    """Find similar events based on type, venue, and characteristics"""
    similar_events = Event.objects.filter(
        Q(event_type=event.event_type) |
        Q(venue=event.venue) |
        Q(sub_category=event.sub_category),
        status='confirmed',
        start_date__gte=datetime.now().date()
    ).exclude(id=event.id).annotate(
        avg_rating=Avg('reviews__rating')
    ).order_by('-avg_rating')[:limit]
    
    return similar_events

def get_trending_events(limit=6):
    """Get trending events based on recent activity"""
    # Events with high registration activity in the last 7 days
    week_ago = datetime.now() - timedelta(days=7)
    
    trending_events = Event.objects.filter(
        status='confirmed',
        start_date__gte=datetime.now().date(),
        registrations__created_at__gte=week_ago
    ).annotate(
        recent_registrations=Count('registrations', filter=Q(registrations__created_at__gte=week_ago))
    ).order_by('-recent_registrations', '-start_date')[:limit]
    
    return trending_events

def get_personalized_recommendations(user, limit=8):
    """Advanced personalized recommendations using multiple factors"""
    if not user.is_authenticated:
        return get_popular_events(limit)
    
    recommendations = []
    
    # 1. Based on user's event history
    user_events = Event.objects.filter(
        registrations__user=user
    ).values_list('event_type_id', flat=True).distinct()
    
    if user_events:
        history_based = Event.objects.filter(
            event_type_id__in=user_events,
            status='confirmed',
            start_date__gte=datetime.now().date()
        ).exclude(
            registrations__user=user
        ).annotate(
            avg_rating=Avg('reviews__rating')
        ).order_by('-avg_rating')[:limit//2]
        recommendations.extend(history_based)
    
    # 2. Based on user's location (if available)
    try:
        user_profile = user.user_profile
        if user_profile.city:
            location_based = Event.objects.filter(
                venue__city__icontains=user_profile.city,
                status='confirmed',
                start_date__gte=datetime.now().date()
            ).exclude(
                registrations__user=user
            ).annotate(
                avg_rating=Avg('reviews__rating')
            ).order_by('-avg_rating')[:limit//4]
            recommendations.extend(location_based)
    except UserProfile.DoesNotExist:
        pass
    
    # 3. Fill remaining slots with popular events
    remaining_limit = limit - len(recommendations)
    if remaining_limit > 0:
        popular_events = get_popular_events(remaining_limit)
        recommendations.extend(popular_events)
    
    # Remove duplicates and return
    seen_ids = set()
    unique_recommendations = []
    for event in recommendations:
        if event.id not in seen_ids:
            seen_ids.add(event.id)
            unique_recommendations.append(event)
    
    return unique_recommendations[:limit]

def get_event_insights(event):
    """Get insights and analytics for an event"""
    total_registrations = event.registrations.count()
    avg_rating = calculate_event_rating(event)
    
    # Calculate registration trend
    registrations_by_day = event.registrations.extra(
        select={'day': 'date(created_at)'}
    ).values('day').annotate(count=Count('id')).order_by('day')
    
    # Calculate revenue
    total_revenue = event.total_cost if event.payment_status == 'paid' else 0
    
    # Get demographic insights (if user data available)
    age_groups = {}
    gender_distribution = {}
    
    for registration in event.registrations.all():
        user = registration.user
        if user.date_of_birth:
            age = (datetime.now().date() - user.date_of_birth).days // 365
            age_group = f"{(age // 10) * 10}-{(age // 10) * 10 + 9}"
            age_groups[age_group] = age_groups.get(age_group, 0) + 1
        
        if user.gender:
            gender_distribution[user.gender] = gender_distribution.get(user.gender, 0) + 1
    
    return {
        'total_registrations': total_registrations,
        'avg_rating': avg_rating,
        'total_revenue': total_revenue,
        'registration_trend': list(registrations_by_day),
        'age_groups': age_groups,
        'gender_distribution': gender_distribution,
        'capacity_utilization': (total_registrations / event.expected_guests * 100) if event.expected_guests > 0 else 0
    }

def predict_event_success(event):
    """Predict event success based on various factors"""
    score = 0
    
    # Factor 1: Event type popularity
    type_popularity = Event.objects.filter(
        event_type=event.event_type,
        status='confirmed'
    ).aggregate(
        avg_registrations=Avg('registrations__id', distinct=True)
    )['avg_registrations'] or 0
    
    if type_popularity > 50:
        score += 25
    elif type_popularity > 20:
        score += 15
    elif type_popularity > 10:
        score += 10
    
    # Factor 2: Venue rating
    venue_rating = event.venue.venue_reviews.aggregate(
        avg_rating=Avg('rating')
    )['avg_rating'] or 0
    
    score += venue_rating * 5
    
    # Factor 3: Time until event
    days_until_event = (event.start_date - datetime.now().date()).days
    if days_until_event > 30:
        score += 20
    elif days_until_event > 14:
        score += 15
    elif days_until_event > 7:
        score += 10
    
    # Factor 4: Pricing competitiveness
    avg_price = Event.objects.filter(
        event_type=event.event_type
    ).aggregate(
        avg_cost=Avg('total_cost')
    )['avg_cost'] or 0
    
    if avg_price > 0:
        price_ratio = event.total_cost / avg_price
        if price_ratio < 0.8:
            score += 20
        elif price_ratio < 1.0:
            score += 15
        elif price_ratio < 1.2:
            score += 10
    
    # Factor 5: Organizer reputation
    organizer_events = Event.objects.filter(
        organizer=event.organizer,
        status='confirmed'
    ).aggregate(
        avg_rating=Avg('reviews__rating')
    )['avg_rating'] or 0
    
    score += organizer_events * 10
    
    # Normalize score to 0-100
    score = min(100, max(0, score))
    
    if score >= 80:
        prediction = "Excellent"
    elif score >= 60:
        prediction = "Good"
    elif score >= 40:
        prediction = "Fair"
    else:
        prediction = "Needs Improvement"
    
    return {
        'score': score,
        'prediction': prediction,
        'factors': {
            'type_popularity': type_popularity,
            'venue_rating': venue_rating,
            'days_until_event': days_until_event,
            'price_competitiveness': avg_price,
            'organizer_reputation': organizer_events
        }
    }

def get_event_recommendations_for_venue(venue, limit=4):
    """Get event recommendations for a specific venue"""
    return Event.objects.filter(
        venue=venue,
        status='confirmed',
        start_date__gte=datetime.now().date()
    ).annotate(
        avg_rating=Avg('reviews__rating')
    ).order_by('-avg_rating', '-start_date')[:limit]

def get_seasonal_recommendations(limit=6):
    """Get seasonal event recommendations"""
    current_month = datetime.now().month
    
    # Define seasonal event types
    seasonal_types = {
        12: ['Christmas', 'New Year', 'Holiday'],
        1: ['New Year', 'Winter'],
        2: ['Valentine', 'Romance'],
        3: ['Spring', 'Easter'],
        4: ['Spring', 'Outdoor'],
        5: ['Summer', 'Outdoor'],
        6: ['Summer', 'Wedding'],
        7: ['Summer', 'Outdoor'],
        8: ['Summer', 'Festival'],
        9: ['Autumn', 'Corporate'],
        10: ['Halloween', 'Autumn'],
        11: ['Thanksgiving', 'Autumn']
    }
    
    seasonal_keywords = seasonal_types.get(current_month, [])
    
    if seasonal_keywords:
        query = Q()
        for keyword in seasonal_keywords:
            query |= Q(title__icontains=keyword) | Q(description__icontains=keyword)
        
        seasonal_events = Event.objects.filter(
            query,
            status='confirmed',
            start_date__gte=datetime.now().date()
        ).annotate(
            avg_rating=Avg('reviews__rating')
        ).order_by('-avg_rating')[:limit]
        
        return seasonal_events
    
    return get_popular_events(limit) 