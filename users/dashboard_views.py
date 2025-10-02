from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from communications.utils import get_allowed_chat_targets
from users import role_required

@login_required
def dashboard_home(request):
    from events.models import Event, Registration
    from venues.models import Venue
    from decimal import Decimal
    from django.utils import timezone
    
    # Get user's events and bookings
    user_events = Event.objects.filter(organizer=request.user)
    user_bookings = Registration.objects.filter(email=request.user.email)
    
    # Calculate statistics
    total_events = user_events.count()
    total_bookings = user_bookings.count()
    total_spent = sum(event.total_cost for event in user_events)
    
    # Get recent events and bookings
    recent_events = user_events.order_by('-created_at')[:5]
    recent_bookings = user_bookings.order_by('-created_at')[:5]
    
    # Get upcoming events
    upcoming_events = user_events.filter(start_date__gte=timezone.now().date()).order_by('start_date')[:5]
    
    allowed_contacts = get_allowed_chat_targets(request.user)
    
    context = {
        'allowed_contacts': allowed_contacts,
        'total_events': total_events,
        'total_bookings': total_bookings,
        'total_spent': total_spent,
        'recent_events': recent_events,
        'recent_bookings': recent_bookings,
        'upcoming_events': upcoming_events,
    }
    return render(request, 'users/dashboard.html', context)

@login_required
def user_events(request):
    from events.models import Event
    from django.core.paginator import Paginator
    
    # Get user's events
    user_events = Event.objects.filter(organizer=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(user_events, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'events': page_obj,
        'total_events': user_events.count(),
    }
    return render(request, 'users/my_events.html', context)

@login_required
def user_bookings(request):
    from events.models import Registration
    from django.core.paginator import Paginator
    
    # Get user's bookings
    user_bookings = Registration.objects.filter(email=request.user.email).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(user_bookings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'bookings': page_obj,
        'total_bookings': user_bookings.count(),
    }
    return render(request, 'users/my_bookings.html', context)

@login_required
def user_payments(request):
    from payments.models import Payment
    from django.core.paginator import Paginator
    
    # Get user's payments
    user_payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(user_payments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'payments': page_obj,
        'total_payments': user_payments.count(),
        'total_paid': sum(payment.amount for payment in user_payments if payment.status == 'completed'),
    }
    return render(request, 'users/my_payments.html', context)

@login_required
def user_messages(request):
    from communications.models import Conversation, Message
    from django.db import models
    
    # Get user's conversations
    conversations = Conversation.objects.filter(
        models.Q(participant1=request.user) | models.Q(participant2=request.user)
    ).order_by('-updated_at')
    
    context = {
        'conversations': conversations,
        'user': request.user,
    }
    return render(request, 'communications/conversation_list.html', context)

@role_required(['manager'])
def manager_dashboard(request):
    from events.models import Event, Registration
    from venues.models import Venue
    from decimal import Decimal
    from django.utils import timezone
    from datetime import timedelta
    
    # Get manager's events
    managed_events = Event.objects.filter(event_manager=request.user)
    
    # Get all registrations for manager's events
    event_ids = managed_events.values_list('id', flat=True)
    all_registrations = Registration.objects.filter(event_id__in=event_ids).select_related('event', 'event__venue').order_by('-created_at')
    
    # Calculate statistics
    total_events_managed = managed_events.count()
    total_revenue = sum(event.total_cost for event in managed_events.filter(status='confirmed'))
    total_clients = managed_events.values('organizer').distinct().count()
    total_bookings = all_registrations.count()
    
    # Get upcoming events
    upcoming_events = managed_events.filter(
        start_date__gte=timezone.now().date()
    ).order_by('start_date')[:5]
    
    # Get today's tasks
    today = timezone.now().date()
    todays_events = managed_events.filter(start_date=today)
    
    # Get recent activity
    recent_events = managed_events.order_by('-created_at')[:5]
    
    # Get recent bookings
    recent_bookings = all_registrations[:10]
    
    context = {
        'total_events_managed': total_events_managed,
        'total_revenue': total_revenue,
        'total_clients': total_clients,
        'total_bookings': total_bookings,
        'upcoming_events': upcoming_events,
        'todays_events': todays_events,
        'recent_events': recent_events,
        'recent_bookings': recent_bookings,
        'events': managed_events,
        'registrations': all_registrations,
    }
    return render(request, 'users/manager_dashboard.html', context)

@role_required(['manager'])
def manager_clients(request):
    from events.models import Event
    from users.models import CustomUser
    from django.db import models
    
    # Get manager's events and their organizers
    managed_events = Event.objects.filter(event_manager=request.user)
    client_ids = managed_events.values_list('organizer', flat=True).distinct()
    clients = CustomUser.objects.filter(id__in=client_ids)
    
    context = {
        'clients': clients,
        'total_clients': clients.count(),
    }
    return render(request, 'users/manager_clients.html', context)

@role_required(['manager'])
def manager_events(request):
    from events.models import Event
    from django.core.paginator import Paginator
    
    # Get manager's events
    managed_events = Event.objects.filter(event_manager=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(managed_events, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'events': page_obj,
        'total_events': managed_events.count(),
    }
    return render(request, 'users/manager_events.html', context)

@role_required(['manager'])
def manager_consultations(request):
    from communications.models import Conversation, Message
    from django.db import models
    
    # Get consultations (conversations with users)
    consultations = Conversation.objects.filter(
        models.Q(participant1=request.user) | models.Q(participant2=request.user)
    ).filter(
        models.Q(participant1__user_type='user') | models.Q(participant2__user_type='user')
    ).order_by('-updated_at')
    
    context = {
        'consultations': consultations,
    }
    return render(request, 'users/manager_consultations.html', context)

@role_required(['manager'])
def manager_earnings(request):
    from events.models import Event
    from payments.models import Payment
    from django.utils import timezone
    from datetime import timedelta
    
    # Get manager's events and payments
    managed_events = Event.objects.filter(event_manager=request.user)
    
    # Calculate earnings
    total_earnings = sum(event.total_cost for event in managed_events.filter(status='confirmed'))
    
    # Get monthly earnings
    monthly_earnings = []
    for i in range(6):
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        month_end = month_start.replace(day=28) + timedelta(days=4)
        month_end = month_end.replace(day=1) - timedelta(days=1)
        
        month_earnings = sum(
            event.total_cost for event in managed_events.filter(
                created_at__gte=month_start,
                created_at__lte=month_end,
                status='confirmed'
            )
        )
        monthly_earnings.append({
            'month': month_start.strftime('%B %Y'),
            'earnings': float(month_earnings)
        })
    
    context = {
        'total_earnings': total_earnings,
        'monthly_earnings': monthly_earnings,
    }
    return render(request, 'users/manager_earnings.html', context)

@role_required(['admin'])
def admin_dashboard(request):
    from events.models import Event, Registration
    from venues.models import Venue
    from users.models import CustomUser
    from decimal import Decimal
    from django.utils import timezone
    from datetime import timedelta
    
    # Get overall statistics
    total_users = CustomUser.objects.filter(user_type='user').count()
    total_managers = CustomUser.objects.filter(user_type='manager').count()
    total_events = Event.objects.count()
    total_venues = Venue.objects.count()
    
    # Calculate revenue
    total_revenue = sum(event.total_cost for event in Event.objects.filter(status='confirmed'))
    
    # Get recent activity
    recent_events = Event.objects.order_by('-created_at')[:10]
    recent_registrations = Registration.objects.order_by('-created_at')[:10]
    
    # Get monthly revenue data for chart
    monthly_revenue = []
    for i in range(6):
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        month_end = month_start.replace(day=28) + timedelta(days=4)
        month_end = month_end.replace(day=1) - timedelta(days=1)
        
        month_revenue = sum(
            event.total_cost for event in Event.objects.filter(
                created_at__gte=month_start,
                created_at__lte=month_end,
                status='confirmed'
            )
        )
        monthly_revenue.append({
            'month': month_start.strftime('%B %Y'),
            'revenue': float(month_revenue)
        })
    
    context = {
        'total_users': total_users,
        'total_managers': total_managers,
        'total_events': total_events,
        'total_venues': total_venues,
        'total_revenue': total_revenue,
        'recent_events': recent_events,
        'recent_registrations': recent_registrations,
        'monthly_revenue': monthly_revenue,
    }
    return render(request, 'users/admin_dashboard.html', context)

@role_required(['admin'])
def admin_users(request):
    from users.models import CustomUser
    from django.core.paginator import Paginator
    
    # Get all users
    users = CustomUser.objects.filter(user_type='user').order_by('-date_joined')
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'users': page_obj,
        'total_users': users.count(),
    }
    return render(request, 'users/admin_users.html', context)

@role_required(['admin'])
def admin_managers(request):
    from users.models import CustomUser
    from django.core.paginator import Paginator
    
    # Get all managers
    managers = CustomUser.objects.filter(user_type='manager').order_by('-date_joined')
    
    # Pagination
    paginator = Paginator(managers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'managers': page_obj,
        'total_managers': managers.count(),
    }
    return render(request, 'users/admin_managers.html', context)

@role_required(['admin'])
def admin_venues(request):
    from venues.models import Venue
    from django.core.paginator import Paginator
    
    # Get all venues
    venues = Venue.objects.all().order_by('-created_at')
    
    # Pagination
    paginator = Paginator(venues, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'venues': page_obj,
        'total_venues': venues.count(),
    }
    return render(request, 'users/admin_venues.html', context)

@role_required(['admin'])
def admin_vendors(request):
    from vendors.models import Vendor
    from django.core.paginator import Paginator
    
    # Get all vendors
    vendors = Vendor.objects.all().order_by('-created_at')
    
    # Pagination
    paginator = Paginator(vendors, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'vendors': page_obj,
        'total_vendors': vendors.count(),
    }
    return render(request, 'users/admin_vendors.html', context)

@role_required(['admin'])
def admin_events(request):
    from events.models import Event
    from django.core.paginator import Paginator
    
    # Get all events
    events = Event.objects.all().order_by('-created_at')
    
    # Pagination
    paginator = Paginator(events, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'events': page_obj,
        'total_events': events.count(),
    }
    return render(request, 'users/admin_events.html', context)

@role_required(['admin'])
def admin_payments(request):
    from payments.models import Payment
    from django.core.paginator import Paginator
    
    # Get all payments
    payments = Payment.objects.all().order_by('-created_at')
    
    # Pagination
    paginator = Paginator(payments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'payments': page_obj,
        'total_payments': payments.count(),
        'total_revenue': sum(payment.amount for payment in payments if payment.status == 'completed'),
    }
    return render(request, 'users/admin_payments.html', context)

@role_required(['admin'])
def admin_reports(request):
    from events.models import Event, Registration
    from payments.models import Payment
    from django.utils import timezone
    from datetime import timedelta
    
    # Generate reports
    total_events = Event.objects.count()
    total_bookings = Registration.objects.count()
    total_revenue = sum(payment.amount for payment in Payment.objects.filter(status='completed'))
    
    # Monthly statistics
    monthly_stats = []
    for i in range(6):
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        month_end = month_start.replace(day=28) + timedelta(days=4)
        month_end = month_end.replace(day=1) - timedelta(days=1)
        
        month_events = Event.objects.filter(created_at__gte=month_start, created_at__lte=month_end).count()
        month_bookings = Registration.objects.filter(created_at__gte=month_start, created_at__lte=month_end).count()
        month_revenue = sum(
            payment.amount for payment in Payment.objects.filter(
                created_at__gte=month_start,
                created_at__lte=month_end,
                status='completed'
            )
        )
        
        monthly_stats.append({
            'month': month_start.strftime('%B %Y'),
            'events': month_events,
            'bookings': month_bookings,
            'revenue': float(month_revenue)
        })
    
    context = {
        'total_events': total_events,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'monthly_stats': monthly_stats,
    }
    return render(request, 'users/admin_reports.html', context)

@login_required
def dashboard(request):
    from events.models import Event, Registration
    from venues.models import Venue
    from decimal import Decimal
    
    # Get user's events and bookings
    user_events = Event.objects.filter(organizer=request.user)
    user_bookings = Registration.objects.filter(email=request.user.email)
    
    # Calculate statistics
    total_events = user_events.count()
    total_bookings = user_bookings.count()
    total_spent = sum(event.total_cost for event in user_events)
    
    # Get recent events and bookings
    recent_events = user_events.order_by('-created_at')[:5]
    recent_bookings = user_bookings.order_by('-created_at')[:5]
    
    # Get upcoming events
    from django.utils import timezone
    upcoming_events = user_events.filter(start_date__gte=timezone.now().date()).order_by('start_date')[:5]
    
    allowed_contacts = get_allowed_chat_targets(request.user)
    
    context = {
        'allowed_contacts': allowed_contacts,
        'total_events': total_events,
        'total_bookings': total_bookings,
        'total_spent': total_spent,
        'recent_events': recent_events,
        'recent_bookings': recent_bookings,
        'upcoming_events': upcoming_events,
    }
    return render(request, 'users/dashboard.html', context) 