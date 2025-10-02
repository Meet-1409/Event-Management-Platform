from django.http import JsonResponse
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Venue, VenueCategory, VenuePackage
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json

class VenueListView(View):
    def get(self, request):
        venues = Venue.objects.filter(status='active').order_by('-is_featured', '-average_rating')
        
        # Search and filtering
        search = request.GET.get('search')
        if search:
            venues = venues.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(city__icontains=search)
            )
            
        category_id = request.GET.get('category')
        if category_id:
            venues = venues.filter(category_id=category_id)
            
        city = request.GET.get('city')
        if city:
            venues = venues.filter(city__iexact=city)
            
        paginator = Paginator(venues, 20)
        page = paginator.get_page(request.GET.get('page', 1))
        
        return JsonResponse({
            "success": True,
            "venues": [{
                "id": venue.id,
                "name": venue.name,
                "slug": venue.slug,
                "category": venue.category.name,
                "address": venue.address,
                "city": venue.city,
                "capacity_min": venue.capacity_min,
                "capacity_max": venue.capacity_max,
                "base_price": float(venue.base_price),
                "average_rating": float(venue.average_rating),
                "total_reviews": venue.total_reviews,
                "is_featured": venue.is_featured,
                "main_image": venue.main_image.image.url if venue.main_image else None
            } for venue in page],
            "pagination": {
                "page": page.number,
                "pages": paginator.num_pages,
                "has_next": page.has_next(),
                "has_previous": page.has_previous()
            }
        })

class VenueDetailView(View):
    def get(self, request, slug):
        try:
            venue = Venue.objects.get(slug=slug, status='active')
            return JsonResponse({
                "success": True,
                "venue": {
                    "id": venue.id,
                    "name": venue.name,
                    "slug": venue.slug,
                    "category": {
                        "id": venue.category.id,
                        "name": venue.category.name
                    },
                    "description": venue.description,
                    "address": venue.address,
                    "city": venue.city,
                    "state": venue.state,
                    "country": str(venue.country),
                    "capacity_min": venue.capacity_min,
                    "capacity_max": venue.capacity_max,
                    "base_price": float(venue.base_price),
                    "price_per_person": float(venue.price_per_person) if venue.price_per_person else None,
                    "deposit_required": float(venue.deposit_required) if venue.deposit_required else None,
                    "features": venue.features,
                    "restrictions": venue.restrictions,
                    "contact_person": venue.contact_person,
                    "contact_phone": venue.contact_phone,
                    "contact_email": venue.contact_email,
                    "website": venue.website,
                    "average_rating": float(venue.average_rating),
                    "total_reviews": venue.total_reviews,
                    "is_featured": venue.is_featured,
                    "images": [{
                        "id": img.id,
                        "image": img.image.url,
                        "caption": img.caption,
                        "is_primary": img.is_primary
                    } for img in venue.images.all()],
                    "packages": [{
                        "id": pkg.id,
                        "name": pkg.name,
                        "description": pkg.description,
                        "price": float(pkg.price),
                        "max_guests": pkg.max_guests,
                        "duration_hours": pkg.duration_hours,
                        "inclusions": pkg.inclusions,
                        "is_popular": pkg.is_popular
                    } for pkg in venue.packages.filter(is_active=True)]
                }
            })
        except Venue.DoesNotExist:
            return JsonResponse({"success": False, "error": "Venue not found"})

class VenueSearchView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        venues = Venue.objects.filter(
            Q(name__icontains=query) | 
            Q(city__icontains=query) | 
            Q(description__icontains=query),
            status='active'
        )[:10]
        
        return JsonResponse({
            "success": True,
            "venues": [{
                "id": venue.id,
                "name": venue.name,
                "city": venue.city,
                "base_price": float(venue.base_price),
                "capacity_max": venue.capacity_max
            } for venue in venues]
        })

class VenueCategoryListView(View):
    def get(self, request):
        categories = VenueCategory.objects.filter(is_active=True)
        return JsonResponse({
            "success": True,
            "categories": [{
                "id": cat.id,
                "name": cat.name,
                "description": cat.description,
                "icon": cat.icon,
                "color": cat.color,
                "venue_count": cat.venues.filter(status='active').count()
            } for cat in categories]
        })

class CategoryVenuesView(View):
    def get(self, request, category_id):
        try:
            category = VenueCategory.objects.get(id=category_id)
            venues = Venue.objects.filter(category=category, status='active')
            
            return JsonResponse({
                "success": True,
                "category": {
                    "id": category.id,
                    "name": category.name,
                    "description": category.description
                },
                "venues": [{
                    "id": venue.id,
                    "name": venue.name,
                    "slug": venue.slug,
                    "base_price": float(venue.base_price),
                    "capacity_max": venue.capacity_max,
                    "city": venue.city,
                    "average_rating": float(venue.average_rating)
                } for venue in venues]
            })
        except VenueCategory.DoesNotExist:
            return JsonResponse({"success": False, "error": "Category not found"})

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class CreateReviewView(View):
    def post(self, request, slug):
        try:
            venue = Venue.objects.get(slug=slug)
            data = json.loads(request.body)
            
            # Create review logic here
            return JsonResponse({
                "success": True,
                "message": "Review submitted successfully"
            })
        except Venue.DoesNotExist:
            return JsonResponse({"success": False, "error": "Venue not found"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

class VenueGalleryEnhancedView(View):
    def get(self, request, slug):
        try:
            venue = Venue.objects.get(slug=slug, status='active')
            return JsonResponse({
                "success": True,
                "venue": {
                    "id": venue.id,
                    "name": venue.name,
                    "images": [{
                        "id": img.id,
                        "image": img.image.url,
                        "caption": img.caption,
                        "is_primary": img.is_primary,
                        "order": img.order
                    } for img in venue.images.all().order_by('order', '-is_primary')]
                }
            })
        except Venue.DoesNotExist:
            return JsonResponse({"success": False, "error": "Venue not found"})

class TourHotspotsView(View):
    def get(self, request, slug):
        try:
            venue = Venue.objects.get(slug=slug, status='active')
            # Mock hotspots data for 360° tour
            hotspots = [
                {"id": 1, "name": "Main Hall", "x": 50, "y": 30, "description": "Spacious main event hall"},
                {"id": 2, "name": "Stage Area", "x": 80, "y": 40, "description": "Professional stage setup"},
                {"id": 3, "name": "Reception", "x": 20, "y": 60, "description": "Welcome reception area"},
            ]
            return JsonResponse({
                "success": True,
                "venue": venue.name,
                "hotspots": hotspots
            })
        except Venue.DoesNotExist:
            return JsonResponse({"success": False, "error": "Venue not found"})

class VenueAvailabilityView(View):
    def get(self, request, slug):
        try:
            venue = Venue.objects.get(slug=slug, status='active')
            # Get availability for next 30 days
            from datetime import date, timedelta
            availability = []
            start_date = date.today()
            for i in range(30):
                current_date = start_date + timedelta(days=i)
                availability.append({
                    "date": current_date.isoformat(),
                    "available": True,  # Simplified - you'd check actual bookings
                    "price": float(venue.base_price)
                })
            
            return JsonResponse({
                "success": True,
                "venue": venue.name,
                "availability": availability
            })
        except Venue.DoesNotExist:
            return JsonResponse({"success": False, "error": "Venue not found"})

class VenueBookingView(View):
    def post(self, request, slug):
        try:
            venue = Venue.objects.get(slug=slug, status='active')
            # Simplified booking logic
            return JsonResponse({
                "success": True,
                "message": f"Booking request received for {venue.name}",
                "booking_id": "BOOK123456"
            })
        except Venue.DoesNotExist:
            return JsonResponse({"success": False, "error": "Venue not found"})

class VenuePackagesView(View):
    def get(self, request, slug):
        try:
            venue = Venue.objects.get(slug=slug, status='active')
            packages = venue.packages.filter(is_active=True)
            return JsonResponse({
                "success": True,
                "packages": [{
                    "id": pkg.id,
                    "name": pkg.name,
                    "description": pkg.description,
                    "price": float(pkg.price),
                    "max_guests": pkg.max_guests,
                    "duration_hours": pkg.duration_hours,
                    "inclusions": pkg.inclusions,
                    "is_popular": pkg.is_popular
                } for pkg in packages]
            })
        except Venue.DoesNotExist:
            return JsonResponse({"success": False, "error": "Venue not found"})

class VenueReviewsView(View):
    def get(self, request, slug):
        try:
            venue = Venue.objects.get(slug=slug, status='active')
            reviews = venue.reviews.filter(is_approved=True).order_by('-created_at')
            return JsonResponse({
                "success": True,
                "reviews": [{
                    "id": review.id,
                    "user": review.user.get_full_name(),
                    "rating": review.rating,
                    "title": review.title,
                    "review_text": review.review_text,
                    "created_at": review.created_at.isoformat()
                } for review in reviews]
            })
        except Venue.DoesNotExist:
            return JsonResponse({"success": False, "error": "Venue not found"})