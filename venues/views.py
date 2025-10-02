from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Venue, VenueCategory, VenuePackage
from users import role_required

@login_required
def venue_list(request):
    """Display list of venues with search and filtering"""
    venues = Venue.objects.filter(status='active').order_by('-is_featured', '-average_rating')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        venues = venues.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    
    # Category filtering
    category_id = request.GET.get('category')
    if category_id:
        venues = venues.filter(category_id=category_id)
    
    # City filtering
    city = request.GET.get('city')
    if city:
        venues = venues.filter(city__iexact=city)
    
    # Capacity filtering
    min_capacity = request.GET.get('min_capacity')
    if min_capacity:
        venues = venues.filter(capacity_max__gte=min_capacity)
    
    # Price filtering
    max_price = request.GET.get('max_price')
    if max_price:
        venues = venues.filter(base_price__lte=max_price)
    
    # Pagination
    paginator = Paginator(venues, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get available categories and cities for filters
    categories = VenueCategory.objects.filter(is_active=True)
    cities = Venue.objects.filter(status='active').values_list('city', flat=True).distinct()
    
    context = {
        'venues': page_obj,
        'categories': categories,
        'cities': cities,
        'search_query': search_query,
        'selected_category': category_id,
        'selected_city': city,
        'selected_min_capacity': min_capacity,
        'selected_max_price': max_price,
    }
    return render(request, 'venues/venue_list.html', context)

@login_required
def venue_detail(request, venue_slug):
    """Display detailed view of a venue"""
    # Try to get venue by slug first, then by ID
    try:
        venue = get_object_or_404(Venue, slug=venue_slug, status='active')
    except:
        # If slug doesn't work, try as ID
        venue = get_object_or_404(Venue, id=venue_slug, status='active')
    
    # Get venue packages
    packages = venue.packages.filter(is_active=True)
    
    # Get reviews (if any)
    reviews = venue.reviews.filter(is_approved=True).order_by('-created_at')[:5]
    
    context = {
        'venue': venue,
        'packages': packages,
        'reviews': reviews,
    }
    return render(request, 'venues/venue_detail.html', context)

@login_required
def venue_search(request):
    """Advanced venue search page"""
    return venue_list(request)

@login_required
def venue_list_by_category(request, category_slug):
    """Display venues filtered by category"""
    category = get_object_or_404(VenueCategory, slug=category_slug, is_active=True)
    venues = Venue.objects.filter(category=category, status='active').order_by('-is_featured', '-average_rating')
    
    # Pagination
    paginator = Paginator(venues, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'venues': page_obj,
        'category': category,
    }
    return render(request, 'venues/venue_list.html', context)

@login_required
def venue_gallery_enhanced(request, venue_slug):
    """Enhanced venue gallery with detailed images and virtual walkthrough"""
    # Try to get venue by slug first, then by ID
    try:
        venue = get_object_or_404(Venue, slug=venue_slug, status='active')
    except:
        # If slug doesn't work, try as ID
        venue = get_object_or_404(Venue, id=venue_slug, status='active')
    
    context = {
        'venue': venue,
    }
    return render(request, 'venues/venue_gallery.html', context)

@login_required
def venue_gallery(request, venue_slug):
    """Venue image gallery"""
    # Try to get venue by slug first, then by ID
    try:
        venue = get_object_or_404(Venue, slug=venue_slug, status='active')
    except:
        # If slug doesn't work, try as ID
        venue = get_object_or_404(Venue, id=venue_slug, status='active')
    
    context = {
        'venue': venue,
    }
    return render(request, 'venues/venue_gallery.html', context)

@login_required
def venue_reviews(request, venue_slug):
    """Venue reviews and ratings"""
    # Try to get venue by slug first, then by ID
    try:
        venue = get_object_or_404(Venue, slug=venue_slug, status='active')
    except:
        # If slug doesn't work, try as ID
        venue = get_object_or_404(Venue, id=venue_slug, status='active')
    
    reviews = venue.reviews.filter(is_approved=True).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'venue': venue,
        'reviews': page_obj,
    }
    return render(request, 'venues/venue_reviews.html', context)

@login_required
def venue_booking(request, venue_slug):
    """Venue booking page"""
    # Try to get venue by slug first, then by ID
    try:
        venue = get_object_or_404(Venue, slug=venue_slug, status='active')
    except:
        # If slug doesn't work, try as ID
        venue = get_object_or_404(Venue, id=venue_slug, status='active')
    
    packages = venue.packages.filter(is_active=True)
    
    context = {
        'venue': venue,
        'packages': packages,
    }
    return render(request, 'venues/venue_booking.html', context)

@login_required
def venue_availability(request, venue_slug):
    """Venue availability calendar"""
    # Try to get venue by slug first, then by ID
    try:
        venue = get_object_or_404(Venue, slug=venue_slug, status='active')
    except:
        # If slug doesn't work, try as ID
        venue = get_object_or_404(Venue, id=venue_slug, status='active')
    
    context = {
        'venue': venue,
    }
    return render(request, 'venues/venue_availability.html', context)

@login_required
def venue_packages(request, venue_slug):
    """Venue packages and pricing"""
    # Try to get venue by slug first, then by ID
    try:
        venue = get_object_or_404(Venue, slug=venue_slug, status='active')
    except:
        # If slug doesn't work, try as ID
        venue = get_object_or_404(Venue, id=venue_slug, status='active')
    
    packages = venue.packages.filter(is_active=True)
    
    context = {
        'venue': venue,
        'packages': packages,
    }
    return render(request, 'venues/venue_packages.html', context)
