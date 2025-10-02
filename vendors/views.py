from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Vendor, VendorCategory, VendorService
from users import role_required

@login_required
def vendor_list(request):
    """Display list of vendors with search and filtering"""
    vendors = Vendor.objects.filter(status='active').order_by('-is_featured', '-average_rating')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        vendors = vendors.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(category__name__icontains=search_query)
        ).distinct()
    
    # Category filtering
    category_id = request.GET.get('category')
    if category_id:
        vendors = vendors.filter(category_id=category_id)
    
    # Service filtering
    service_id = request.GET.get('service')
    if service_id:
        vendors = vendors.filter(vendor_services__id=service_id)
    
    # City filtering
    city = request.GET.get('city')
    if city:
        vendors = vendors.filter(city__iexact=city)
    
    # Price filtering
    max_price = request.GET.get('max_price')
    if max_price:
        vendors = vendors.filter(minimum_order__lte=max_price)
    
    # Pagination
    paginator = Paginator(vendors, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get available categories and services for filters
    categories = VendorCategory.objects.filter(is_active=True)
    services = VendorService.objects.filter(is_available=True)
    cities = Vendor.objects.filter(status='active').values_list('city', flat=True).distinct()
    
    context = {
        'vendors': page_obj,
        'categories': categories,
        'services': services,
        'cities': cities,
        'search_query': search_query,
        'selected_category': category_id,
        'selected_service': service_id,
        'selected_city': city,
        'selected_max_price': max_price,
    }
    return render(request, 'vendors/vendor_list.html', context)

@login_required
def vendor_detail(request, vendor_slug):
    """Display detailed view of a vendor"""
    # Try to get vendor by slug first, then by ID
    try:
        vendor = get_object_or_404(Vendor, slug=vendor_slug, status='active')
    except:
        # If slug doesn't work, try as ID
        vendor = get_object_or_404(Vendor, id=vendor_slug, status='active')
    
    # Get vendor services
    services = vendor.vendor_services.filter(is_available=True)
    
    # Get reviews (if any)
    reviews = vendor.reviews.filter(is_approved=True).order_by('-created_at')[:5]
    
    context = {
        'vendor': vendor,
        'services': services,
        'reviews': reviews,
    }
    return render(request, 'vendors/vendor_detail.html', context)
