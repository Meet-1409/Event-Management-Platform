from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from .models import Event, EventType, EventGuest, EventTimeline, EventChecklist, EventReview, Registration
from .forms import EventCreationForm, EventGuestForm, EventTimelineForm, EventChecklistForm, EventSearchForm, EventReviewForm
from .utils import generate_pdf_invoice
from venues.models import Venue
from users import role_required
import uuid

@login_required
def event_list(request):
    """Display list of events with search and filtering"""
    # Only show public events that are appropriate for users to join
    # Exclude private events like birthdays, weddings, corporate events
    events = Event.objects.filter(
        is_public=True,
        event_type__name__in=['Sports', 'Sports Tournament', 'Workshop', 'Cultural Festival', 'Music', 'Adventure']
    ).order_by('-created_at')
    
    # Search and filtering
    search_form = EventSearchForm(request.GET)
    if search_form.is_valid():
        if search_form.cleaned_data.get('event_type'):
            events = events.filter(event_type=search_form.cleaned_data['event_type'])
        if search_form.cleaned_data.get('start_date'):
            events = events.filter(start_date__gte=search_form.cleaned_data['start_date'])
        if search_form.cleaned_data.get('end_date'):
            events = events.filter(end_date__lte=search_form.cleaned_data['end_date'])
        if search_form.cleaned_data.get('venue'):
            events = events.filter(venue=search_form.cleaned_data['venue'])
        if search_form.cleaned_data.get('min_guests'):
            events = events.filter(expected_guests__gte=search_form.cleaned_data['min_guests'])
        if search_form.cleaned_data.get('max_budget'):
            events = events.filter(total_budget__lte=search_form.cleaned_data['max_budget'])
    
    # Pagination
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get available event types for filters (only public event types)
    event_types = EventType.objects.filter(
        is_active=True,
        name__in=['Sports', 'Sports Tournament', 'Workshop', 'Cultural Festival', 'Music', 'Adventure']
    )
    
    # Get available venues for filters
    venues = Venue.objects.filter(status='active')
    
    context = {
        'events': page_obj,
        'search_form': search_form,
        'event_types': event_types,
        'venues': venues,
    }
    return render(request, 'events/event_list.html', context)

@login_required
def event_detail(request, event_id):
    """Display detailed view of an event"""
    event = get_object_or_404(Event, id=event_id)
    
    # For public events, any user can view them
    # For private events, only organizer, event manager, or admin/manager can view
    if not event.is_public and not (request.user == event.organizer or request.user == event.event_manager or request.user.user_type in ['admin', 'manager']):
        messages.error(request, 'You do not have permission to view this private event.')
        return redirect('events:event_list')
    
    context = {
        'event': event,
        'guests': event.guests.all(),
        'timeline': event.timeline.all(),
        'checklist': event.checklist.all(),
        'vendors': event.vendors.all(),
    }
    return render(request, 'events/event_detail.html', context)

@role_required(['manager', 'admin'])
def create_event(request):
    """Create a new event - Only managers and admins can create events"""
    if request.method == 'POST':
        form = EventCreationForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.event_id = f"EVT{uuid.uuid4().hex[:8].upper()}"
            
            # Calculate costs
            if event.venue_package:
                event.venue_cost = event.venue_package.price
            else:
                event.venue_cost = 0
            
            event.total_cost = event.venue_cost + event.vendor_costs + event.manager_fee
            event.save()
            
            messages.success(request, 'Event created successfully!')
            return redirect('events:event_detail', event_id=event.id)
    else:
        form = EventCreationForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'Create New Event',
    }
    return render(request, 'events/event_form.html', context)

@login_required
def edit_event(request, event_id):
    """Edit an existing event"""
    event = get_object_or_404(Event, id=event_id)
    
    # Check permissions
    if not (request.user == event.organizer or request.user.user_type in ['admin', 'manager']):
        messages.error(request, 'You do not have permission to edit this event.')
        return redirect('events:event_detail', event_id=event.id)
    
    if request.method == 'POST':
        form = EventCreationForm(request.POST, request.FILES, instance=event, user=request.user)
        if form.is_valid():
            event = form.save(commit=False)
            
            # Recalculate costs
            if event.venue_package:
                event.venue_cost = event.venue_package.price
            else:
                event.venue_cost = 0
            
            event.total_cost = event.venue_cost + event.vendor_costs + event.manager_fee
            event.save()
            
            messages.success(request, 'Event updated successfully!')
            return redirect('events:event_detail', event_id=event.id)
    else:
        form = EventCreationForm(instance=event, user=request.user)
    
    context = {
        'form': form,
        'event': event,
        'title': 'Edit Event',
    }
    return render(request, 'events/event_form.html', context)

@login_required
def delete_event(request, event_id):
    """Delete an event"""
    event = get_object_or_404(Event, id=event_id)
    
    # Check permissions
    if not (request.user == event.organizer or request.user.user_type in ['admin']):
        messages.error(request, 'You do not have permission to delete this event.')
        return redirect('events:event_detail', event_id=event.id)
    
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('events:event_list')
    
    context = {
        'event': event,
    }
    return render(request, 'events/event_confirm_delete.html', context)

@login_required
def add_guest(request, event_id):
    """Add a guest to an event"""
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        form = EventGuestForm(request.POST)
        if form.is_valid():
            guest = form.save(commit=False)
            guest.event = event
            guest.save()
            messages.success(request, 'Guest added successfully!')
            return redirect('events:event_detail', event_id=event.id)
    else:
        form = EventGuestForm()
    
    context = {
        'form': form,
        'event': event,
    }
    return render(request, 'events/guest_form.html', context)

@login_required
def add_timeline_item(request, event_id):
    """Add a timeline item to an event"""
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        form = EventTimelineForm(request.POST)
        if form.is_valid():
            timeline_item = form.save(commit=False)
            timeline_item.event = event
            timeline_item.save()
            messages.success(request, 'Timeline item added successfully!')
            return redirect('events:event_detail', event_id=event.id)
    else:
        form = EventTimelineForm()
    
    context = {
        'form': form,
        'event': event,
    }
    return render(request, 'events/timeline_form.html', context)

@login_required
def add_checklist_item(request, event_id):
    """Add a checklist item to an event"""
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        form = EventChecklistForm(request.POST)
        if form.is_valid():
            checklist_item = form.save(commit=False)
            checklist_item.event = event
            checklist_item.save()
            messages.success(request, 'Checklist item added successfully!')
            return redirect('events:event_detail', event_id=event.id)
    else:
        form = EventChecklistForm()
    
    context = {
        'form': form,
        'event': event,
    }
    return render(request, 'events/checklist_form.html', context)

@login_required
def toggle_checklist_item(request, item_id):
    """Toggle completion status of a checklist item"""
    if request.method == 'POST':
        item = get_object_or_404(EventChecklist, id=item_id)
        item.is_completed = not item.is_completed
        if item.is_completed:
            item.completed_by = request.user.get_full_name() or request.user.username
        item.save()
        return JsonResponse({'success': True, 'is_completed': item.is_completed})
    return JsonResponse({'success': False})

@login_required
def my_events(request):
    """Display events organized by the current user"""
    events = Event.objects.filter(organizer=request.user).order_by('-created_at')
    
    context = {
        'events': events,
        'title': 'My Events',
    }
    return render(request, 'events/my_events.html', context)

@role_required(['admin', 'manager'])
def manage_events(request):
    """Admin/Manager view for managing all events"""
    events = Event.objects.all().order_by('-created_at')
    
    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        events = events.filter(status=status)
    
    context = {
        'events': events,
        'title': 'Manage Events',
    }
    return render(request, 'events/manage_events.html', context)

@login_required
def add_review(request, event_id):
    """Add a review to an event"""
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)
        
        # Check if user has already reviewed this event
        existing_review = EventReview.objects.filter(event=event, user=request.user).first()
        if existing_review:
            return JsonResponse({
                'success': False,
                'error': 'You have already reviewed this event.'
            })
        
        # Create new review
        review = EventReview.objects.create(
            event=event,
            user=request.user,
            rating=request.POST.get('rating'),
            title=request.POST.get('title'),
            comment=request.POST.get('comment')
        )
        
        # Auto-approve for now (can be changed to require admin approval)
        review.is_approved = True
        review.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Review submitted successfully!'
        })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method.'
    })

@login_required
def download_invoice(request, event_id):
    """Download PDF invoice for event"""
    event = get_object_or_404(Event, id=event_id)
    
    # Check if user has permission to download this invoice
    if not (request.user == event.organizer or request.user.user_type in ['admin', 'manager']):
        messages.error(request, 'You do not have permission to download this invoice.')
        return redirect('events:event_detail', event_id=event.id)
    
    # Generate PDF invoice
    response = generate_pdf_invoice(event, request.user)
    
    if response:
        response['Content-Disposition'] = f'attachment; filename="invoice_{event.id}.pdf"'
        return response
    else:
        messages.error(request, 'Error generating invoice. Please try again.')
        return redirect('events:event_detail', event_id=event.id)

@role_required(['admin', 'manager'])
def calendar_view(request):
    """Calendar view for managers and admins"""
    events = Event.objects.all().order_by('-start_date')
    event_types = EventType.objects.filter(is_active=True)
    venues = Venue.objects.filter(status='active')
    
    context = {
        'events': events,
        'event_types': event_types,
        'venues': venues,
    }
    return render(request, 'events/calendar_view.html', context)

@login_required
def cancel_booking(request, booking_id):
    """Cancel a booking"""
    from django.http import JsonResponse
    from django.views.decorators.http import require_POST
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        booking = Registration.objects.get(id=booking_id, email=request.user.email)
        
        # Check if booking can be cancelled (not too close to event date)
        from django.utils import timezone
        days_until_event = (booking.event.start_date - timezone.now().date()).days
        
        if days_until_event < 1:
            return JsonResponse({
                'success': False, 
                'error': 'Cannot cancel booking within 24 hours of the event'
            })
        
        # Update booking status
        booking.status = 'cancelled'
        booking.cancelled_at = timezone.now()
        booking.save()
        
        # Send cancellation email
        try:
            from django.core.mail import send_mail
            send_mail(
                f'Booking Cancelled - {booking.event.title}',
                f'Your booking for {booking.event.title} has been cancelled successfully.',
                'noreply@360eventmanager.com',
                [booking.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send cancellation email: {e}")
        
        return JsonResponse({'success': True, 'message': 'Booking cancelled successfully'})
        
    except Registration.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Booking not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def event_registration(request, event_id):
    """Handle event registration"""
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        # Handle registration form submission
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        guest_count = int(request.POST.get('guest_count', 1))
        special_requirements = request.POST.get('special_requirements', '')
        source = request.POST.get('source', '')
        terms_accepted = request.POST.get('terms') == 'on'
        
        # Create booking record
        from events.models import Registration
        booking = Registration.objects.create(
            event=event,
            name=full_name,
            email=email,
            phone=phone,
            guest_count=guest_count,
            special_requirements=special_requirements,
            source=source,
            terms_accepted=terms_accepted
        )
        
        messages.success(request, f'Successfully registered for {event.title}!')
        return redirect('events:registration_success', booking_id=booking.id)
    
    context = {
        'event': event,
    }
    return render(request, 'events/new_3step_registration.html', context)

@login_required
def registration_success(request, booking_id):
    """Show registration success page"""
    booking = get_object_or_404(Registration, id=booking_id)
    
    context = {
        'booking': booking,
    }
    return render(request, 'events/registration_success.html', context)

@login_required
def event_gallery(request, event_id):
    """Display event gallery with reviews and ratings"""
    event = get_object_or_404(Event, id=event_id)
    
    # Get reviews for this event
    reviews = event.reviews.filter(is_approved=True).order_by('-created_at')
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    total_reviews = reviews.count()
    
    # Get rating distribution with percentages
    rating_distribution = {}
    for i in range(1, 6):
        count = reviews.filter(rating=i).count()
        percentage = (count / total_reviews * 100) if total_reviews > 0 else 0
        rating_distribution[i] = {
            'count': count,
            'percentage': round(percentage, 1)
        }
    
    # Check if user has already reviewed this event
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
    
    # Paginate reviews
    paginator = Paginator(reviews, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'event': event,
        'reviews': page_obj,
        'avg_rating': round(avg_rating, 1),
        'total_reviews': total_reviews,
        'rating_distribution': rating_distribution,
        'user_review': user_review,
        'review_form': EventReviewForm(),
    }
    return render(request, 'events/event_gallery.html', context)

@login_required
def submit_review(request, event_id):
    """Submit a new review for an event"""
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)
        form = EventReviewForm(request.POST)
        
        if form.is_valid():
            # Check if user has already reviewed this event
            existing_review = EventReview.objects.filter(event=event, user=request.user).first()
            if existing_review:
                return JsonResponse({
                    'success': False,
                    'error': 'You have already reviewed this event.'
                })
            
            # Create new review
            review = form.save(commit=False)
            review.event = event
            review.user = request.user
            review.is_approved = True  # Auto-approve for now
            review.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Review submitted successfully!',
                'review': {
                    'id': review.id,
                    'rating': review.rating,
                    'title': review.title,
                    'comment': review.comment,
                    'user_name': review.user.get_full_name() or review.user.username,
                    'created_at': review.created_at.strftime('%B %d, %Y'),
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Please correct the errors in your review.',
                'form_errors': form.errors
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method.'
    })

@login_required
def edit_review(request, review_id):
    """Edit an existing review"""
    review = get_object_or_404(EventReview, id=review_id, user=request.user)
    
    if request.method == 'POST':
        form = EventReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'message': 'Review updated successfully!'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Please correct the errors in your review.',
                'form_errors': form.errors
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method.'
    })

@login_required
def delete_review(request, review_id):
    """Delete a user's own review"""
    review = get_object_or_404(EventReview, id=review_id, user=request.user)
    
    if request.method == 'POST':
        review.delete()
        return JsonResponse({
            'success': True,
            'message': 'Review deleted successfully!'
        })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method.'
    })

@login_required
def get_reviews(request, event_id):
    """Get reviews for an event via AJAX"""
    event = get_object_or_404(Event, id=event_id)
    page = request.GET.get('page', 1)
    
    reviews = event.reviews.filter(is_approved=True).order_by('-created_at')
    paginator = Paginator(reviews, 5)
    
    try:
        page_obj = paginator.page(page)
    except:
        page_obj = paginator.page(1)
    
    reviews_data = []
    for review in page_obj:
        reviews_data.append({
            'id': review.id,
            'rating': review.rating,
            'title': review.title,
            'comment': review.comment,
            'user_name': review.user.get_full_name() or review.user.username,
            'user_avatar': review.user.profile_picture.url if review.user.profile_picture else None,
            'created_at': review.created_at.strftime('%B %d, %Y'),
            'can_edit': review.user == request.user,
        })
    
    return JsonResponse({
        'success': True,
        'reviews': reviews_data,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
    })

@login_required
def event_categories(request):
    """Display event categories"""
    event_types = EventType.objects.filter(is_active=True)
    
    context = {
        'event_types': event_types,
    }
    return render(request, 'events/event_categories.html', context)

@login_required
def adventure_events(request):
    """Display adventure events"""
    events = Event.objects.filter(
        event_type__name__in=['Adventure', 'Sports'],
        is_public=True
    ).order_by('start_date')
    
    context = {
        'events': events,
        'category': 'Adventure'
    }
    return render(request, 'events/adventure_events.html', context)

@login_required
def movie_events(request):
    """Display movie events"""
    events = Event.objects.filter(
        event_type__name__in=['Entertainment', 'Cultural Festival'],
        is_public=True
    ).order_by('start_date')
    
    context = {
        'events': events,
        'category': 'Movie'
    }
    return render(request, 'events/movie_events.html', context)

@login_required
def music_events(request):
    """Display music events"""
    events = Event.objects.filter(
        event_type__name__in=['Music', 'Cultural Festival'],
        is_public=True
    ).order_by('start_date')
    
    context = {
        'events': events,
        'category': 'Music'
    }
    return render(request, 'events/music_events_simple.html', context)

@login_required
def cooking_events(request):
    """Display cooking events"""
    events = Event.objects.filter(
        event_type__name__in=['Workshop', 'Cultural Festival'],
        is_public=True
    ).order_by('start_date')
    
    context = {
        'events': events,
        'category': 'Cooking'
    }
    return render(request, 'events/cooking_events.html', context)

@login_required
def coding_events(request):
    """Display coding events"""
    events = Event.objects.filter(
        event_type__name__in=['Workshop', 'Technology'],
        is_public=True
    ).order_by('start_date')
    
    context = {
        'events': events,
        'category': 'Coding'
    }
    return render(request, 'events/coding_events.html', context)

@login_required
def sports_events(request):
    """Display sports events"""
    events = Event.objects.filter(
        event_type__name__in=['Sports', 'Sports Tournament'],
        is_public=True
    ).order_by('start_date')
    
    context = {
        'events': events,
        'category': 'Sports'
    }
    return render(request, 'events/sports_events.html', context)

@login_required
def booking_page(request, event_id):
    """Display booking page for an event"""
    event = get_object_or_404(Event, id=event_id)
    
    context = {
        'event': event,
    }
    return render(request, 'events/booking_page.html', context)

@login_required
def generate_invoice(request, booking_id):
    """Generate invoice for a booking"""
    from events.models import Registration
    
    booking = get_object_or_404(Registration, id=booking_id)
    
    # Generate PDF invoice
    pdf_response = generate_pdf_invoice(booking)
    
    return pdf_response

@login_required
def reviews_section(request, event_id):
    """Display reviews for an event"""
    event = get_object_or_404(Event, id=event_id)
    reviews = event.reviews.all().order_by('-created_at')
    
    context = {
        'event': event,
        'reviews': reviews,
    }
    return render(request, 'events/reviews_section.html', context)
