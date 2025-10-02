from django.http import JsonResponse
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Vendor, VendorCategory, VendorService
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class VendorListView(View):
    def get(self, request):
        vendors = Vendor.objects.filter(status__in=['active', 'verified']).order_by('-is_featured', '-average_rating')
        
        # Filtering
        category_id = request.GET.get('category')
        if category_id:
            vendors = vendors.filter(category_id=category_id)
            
        city = request.GET.get('city')
        if city:
            vendors = vendors.filter(city__iexact=city)
            
        search = request.GET.get('search')
        if search:
            vendors = vendors.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(business_name__icontains=search)
            )
            
        paginator = Paginator(vendors, 20)
        page = paginator.get_page(request.GET.get('page', 1))
        
        return JsonResponse({
            "success": True,
            "vendors": [{
                "id": vendor.id,
                "name": vendor.name,
                "slug": vendor.slug,
                "business_name": vendor.business_name,
                "category": vendor.category.name,
                "city": vendor.city,
                "description": vendor.description[:200] + "..." if len(vendor.description) > 200 else vendor.description,
                "contact_phone": vendor.contact_phone,
                "contact_email": vendor.contact_email,
                "years_in_business": vendor.years_in_business,
                "average_rating": float(vendor.average_rating),
                "total_reviews": vendor.total_reviews,
                "total_events_served": vendor.total_events_served,
                "is_verified": vendor.is_verified,
                "is_featured": vendor.is_featured,
                "is_available": vendor.is_available,
                "profile_image": vendor.profile_image.url if vendor.profile_image else None,
                "minimum_order": float(vendor.minimum_order) if vendor.minimum_order else None,
                "service_areas": vendor.service_areas,
                "is_premium": vendor.is_premium
            } for vendor in page],
            "pagination": {
                "page": page.number,
                "pages": paginator.num_pages,
                "has_next": page.has_next(),
                "has_previous": page.has_previous()
            }
        })

class VendorDetailView(View):
    def get(self, request, slug):
        try:
            vendor = Vendor.objects.get(slug=slug, status__in=['active', 'verified'])
            return JsonResponse({
                "success": True,
                "vendor": {
                    "id": vendor.id,
                    "name": vendor.name,
                    "slug": vendor.slug,
                    "business_name": vendor.business_name,
                    "category": {
                        "id": vendor.category.id,
                        "name": vendor.category.name,
                        "description": vendor.category.description
                    },
                    "description": vendor.description,
                    "bio": vendor.bio,
                    "contact": {
                        "person": vendor.contact_person,
                        "phone": vendor.contact_phone,
                        "email": vendor.contact_email,
                        "website": vendor.website
                    },
                    "location": {
                        "address": vendor.address,
                        "city": vendor.city,
                        "state": vendor.state,
                        "country": str(vendor.country),
                        "postal_code": vendor.postal_code,
                        "service_areas": vendor.service_areas,
                        "travel_radius": vendor.travel_radius
                    },
                    "business_info": {
                        "license": vendor.business_license,
                        "tax_id": vendor.tax_id,
                        "years_in_business": vendor.years_in_business
                    },
                    "services": vendor.services,
                    "pricing_info": vendor.pricing_info,
                    "minimum_order": float(vendor.minimum_order) if vendor.minimum_order else None,
                    "availability": {
                        "schedule": vendor.availability_schedule,
                        "max_events_per_day": vendor.max_events_per_day,
                        "is_available": vendor.is_available
                    },
                    "performance": {
                        "total_events_served": vendor.total_events_served,
                        "average_rating": float(vendor.average_rating),
                        "total_reviews": vendor.total_reviews,
                        "success_rate": float(vendor.success_rate)
                    },
                    "status": {
                        "status": vendor.status,
                        "is_verified": vendor.is_verified,
                        "is_featured": vendor.is_featured,
                        "verification_date": vendor.verification_date.isoformat() if vendor.verification_date else None
                    },
                    "profile_image": vendor.profile_image.url if vendor.profile_image else None,
                    "images": [{
                        "id": img.id,
                        "image": img.image.url,
                        "caption": img.caption,
                        "is_primary": img.is_primary
                    } for img in vendor.images.all()],
                    "vendor_services": [{
                        "id": service.id,
                        "name": service.name,
                        "description": service.description,
                        "price": float(service.price) if service.price else None,
                        "price_type": service.price_type,
                        "is_available": service.is_available
                    } for service in vendor.vendor_services.filter(is_available=True)],
                    "packages": [{
                        "id": pkg.id,
                        "name": pkg.name,
                        "description": pkg.description,
                        "price": float(pkg.price),
                        "max_guests": pkg.max_guests,
                        "duration_hours": pkg.duration_hours,
                        "inclusions": pkg.inclusions,
                        "exclusions": pkg.exclusions,
                        "is_popular": pkg.is_popular
                    } for pkg in vendor.packages.filter(is_active=True)],
                    "specializations": [{
                        "name": spec.name,
                        "description": spec.description,
                        "years_experience": spec.years_experience
                    } for spec in vendor.specializations.all()],
                    "is_premium": vendor.is_premium,
                    "is_available_for_booking": vendor.is_available_for_booking
                }
            })
        except Vendor.DoesNotExist:
            return JsonResponse({"success": False, "error": "Vendor not found"})

class VendorCategoryListView(View):
    def get(self, request):
        categories = VendorCategory.objects.filter(is_active=True)
        return JsonResponse({
            "success": True,
            "categories": [{
                "id": cat.id,
                "name": cat.name,
                "description": cat.description,
                "icon": cat.icon,
                "color": cat.color,
                "vendor_count": cat.vendors.filter(status__in=['active', 'verified']).count()
            } for cat in categories]
        })

class VendorSearchView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        vendors = Vendor.objects.filter(
            Q(name__icontains=query) | 
            Q(business_name__icontains=query) | 
            Q(city__icontains=query) |
            Q(category__name__icontains=query),
            status__in=['active', 'verified']
        )[:10]
        
        return JsonResponse({
            "success": True,
            "vendors": [{
                "id": vendor.id,
                "name": vendor.name,
                "business_name": vendor.business_name,
                "category": vendor.category.name,
                "city": vendor.city,
                "average_rating": float(vendor.average_rating),
                "is_verified": vendor.is_verified
            } for vendor in vendors]
        })

class CategoryVendorsView(View):
    def get(self, request, category_id):
        try:
            category = VendorCategory.objects.get(id=category_id)
            vendors = Vendor.objects.filter(
                category=category,
                status__in=['active', 'verified']
            ).order_by('-is_featured', '-average_rating')
            
            return JsonResponse({
                "success": True,
                "category": {
                    "id": category.id,
                    "name": category.name,
                    "description": category.description
                },
                "vendors": [{
                    "id": vendor.id,
                    "name": vendor.name,
                    "business_name": vendor.business_name,
                    "city": vendor.city,
                    "average_rating": float(vendor.average_rating),
                    "total_events_served": vendor.total_events_served,
                    "is_verified": vendor.is_verified,
                    "is_featured": vendor.is_featured,
                    "profile_image": vendor.profile_image.url if vendor.profile_image else None
                } for vendor in vendors]
            })
        except VendorCategory.DoesNotExist:
            return JsonResponse({"success": False, "error": "Category not found"})