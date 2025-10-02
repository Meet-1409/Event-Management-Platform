from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.utils import timezone
from .forms import ManagerCreationForm, ManagerAuthenticationForm
from users.models import CustomUser
from django.contrib.auth.decorators import login_required
from users import role_required

# Redirect functions for manager authentication
def login_view(request):
    """Redirect manager login to main user login"""
    return redirect('users:login')

def register_view(request):
    """Redirect manager registration to main user registration"""
    return redirect('users:register')

def dashboard_view(request):
    """Redirect to manager dashboard"""
    if request.user.is_authenticated and request.user.user_type == 'manager':
        return redirect('users:manager_dashboard')
    return redirect('users:login')

def manager_list(request):
    """Display list of event managers"""
    managers = CustomUser.objects.filter(
        user_type='manager',
        is_active=True
    ).select_related('manager_profile').order_by('-date_joined')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        managers = managers.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(city__icontains=search_query)
        )
    
    # Filter by verification status
    verification_filter = request.GET.get('verified')
    if verification_filter == 'yes':
        managers = managers.filter(manager_profile__is_verified=True)
    elif verification_filter == 'no':
        managers = managers.filter(manager_profile__is_verified=False)
    
    # Filter by city
    city_filter = request.GET.get('city')
    if city_filter:
        managers = managers.filter(city__iexact=city_filter)
    
    # Filter by specialization
    specialization_filter = request.GET.get('specialization')
    if specialization_filter:
        managers = managers.filter(manager_profile__specializations__contains=[specialization_filter])
    
    # Pagination
    paginator = Paginator(managers, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    cities = CustomUser.objects.filter(user_type='manager', is_active=True).values_list('city', flat=True).distinct()
    
    # Get all specializations
    specializations = set()
    for manager in CustomUser.objects.filter(user_type='manager'):
        if hasattr(manager, 'manager_profile') and manager.manager_profile.specializations:
            specializations.update(manager.manager_profile.specializations)
    
    context = {
        'managers': page_obj,
        'search_query': search_query,
        'verification_filter': verification_filter,
        'city_filter': city_filter,
        'specialization_filter': specialization_filter,
        'cities': cities,
        'specializations': sorted(list(specializations)),
        'total_managers': managers.count(),
    }
    return render(request, 'managers/manager_list.html', context)

def manager_detail(request, manager_slug):
    """Display detailed view of an event manager"""
    try:
        # Try to get by ID first, then by username as slug
        try:
            manager = get_object_or_404(CustomUser, id=manager_slug, user_type='manager')
        except (ValueError, CustomUser.DoesNotExist):
            manager = get_object_or_404(CustomUser, username=manager_slug, user_type='manager')
    except CustomUser.DoesNotExist:
        messages.error(request, 'Manager not found.')
        return redirect('managers:manager_list')
    
    # Get manager profile
    manager_profile = None
    if hasattr(manager, 'manager_profile'):
        manager_profile = manager.manager_profile
    
    # Get managed events
    managed_events = manager.managed_events.all().order_by('-created_at')[:6]
    
    # Get reviews/ratings for this manager
    event_reviews = []
    for event in manager.managed_events.filter(status='completed'):
        reviews = event.reviews.filter(is_approved=True)
        event_reviews.extend(reviews)
    
    # Calculate average rating from event reviews
    if event_reviews:
        avg_rating = sum(review.rating for review in event_reviews) / len(event_reviews)
        total_reviews = len(event_reviews)
    else:
        avg_rating = manager_profile.average_rating if manager_profile else 0
        total_reviews = manager_profile.total_reviews if manager_profile else 0
    
    # Get statistics
    stats = {
        'total_events': manager.managed_events.count(),
        'completed_events': manager.managed_events.filter(status='completed').count(),
        'upcoming_events': manager.managed_events.filter(status__in=['confirmed', 'in_progress']).count(),
        'avg_rating': round(avg_rating, 1),
        'total_reviews': total_reviews,
        'years_experience': manager_profile.years_of_experience if manager_profile else 0,
        'specializations': manager_profile.specializations if manager_profile else [],
        'service_areas': manager_profile.service_areas if manager_profile else []
    }
    
    context = {
        'manager': manager,
        'manager_profile': manager_profile,
        'managed_events': managed_events,
        'stats': stats,
        'recent_reviews': event_reviews[:5],  # Show last 5 reviews
    }
    return render(request, 'managers/manager_detail.html', context)

@role_required(['admin'])
def manager_verification(request):
    """Admin view for manager verification"""
    pending_managers = CustomUser.objects.filter(
        user_type='manager',
        manager_profile__is_verified=False
    ).select_related('manager_profile')
    
    context = {
        'pending_managers': pending_managers,
    }
    return render(request, 'managers/manager_verification.html', context)

@role_required(['admin'])
def verify_manager(request, manager_id):
    """Verify a manager (admin only)"""
    if request.method == 'POST':
        manager = get_object_or_404(CustomUser, id=manager_id, user_type='manager')
        
        if hasattr(manager, 'manager_profile'):
            manager.manager_profile.is_verified = True
            manager.manager_profile.verified_by = request.user
            manager.manager_profile.verification_date = timezone.now()
            manager.manager_profile.save()
            
            messages.success(request, f'Manager {manager.get_full_name()} has been verified successfully.')
        else:
            messages.error(request, 'Manager profile not found.')
    
    return redirect('managers:manager_verification')

def manager_specializations(request):
    """Display all manager specializations"""
    specializations = set()
    managers = CustomUser.objects.filter(user_type='manager', is_active=True)
    
    for manager in managers:
        if hasattr(manager, 'manager_profile') and manager.manager_profile.specializations:
            specializations.update(manager.manager_profile.specializations)
    
    specialization_data = []
    for spec in sorted(list(specializations)):
        count = 0
        for manager in managers:
            if hasattr(manager, 'manager_profile') and spec in (manager.manager_profile.specializations or []):
                count += 1
        specialization_data.append({
            'name': spec,
            'count': count
        })
    
    context = {
        'specializations': specialization_data,
    }
    return render(request, 'managers/specializations.html', context)

@login_required
def contact_manager(request, manager_id):
    """Contact form for reaching out to a manager"""
    manager = get_object_or_404(CustomUser, id=manager_id, user_type='manager')
    
    if request.method == 'POST':
        # Create a conversation or send message
        from communications.models import Conversation
        from django.utils import timezone
        
        # Get or create conversation
        user1, user2 = (request.user, manager) if request.user.id < manager.id else (manager, request.user)
        conversation, created = Conversation.objects.get_or_create(
            participant1=user1,
            participant2=user2,
            defaults={
                'conversation_type': 'user_manager',
                'last_message_at': timezone.now()
            }
        )
        
        messages.success(request, f'You can now chat with {manager.get_full_name()}!')
        return redirect('communications:chat_room', conversation_id=conversation.id)
    
    context = {
        'manager': manager,
    }
    return render(request, 'managers/contact_manager.html', context)