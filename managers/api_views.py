from django.http import JsonResponse
from django.views import View
from django.core.paginator import Paginator
from users.models import CustomUser
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class ManagerListView(View):
    def get(self, request):
        managers = CustomUser.objects.filter(
            user_type='manager',
            is_active=True
        ).order_by('-date_joined')
        
        paginator = Paginator(managers, 20)
        page = paginator.get_page(request.GET.get('page', 1))
        
        return JsonResponse({
            "success": True,
            "managers": [{
                "id": manager.id,
                "name": manager.get_full_name(),
                "email": manager.email,
                "phone_number": manager.phone_number,
                "city": manager.city,
                "date_joined": manager.date_joined.isoformat(),
                "profile": {
                    "company_name": manager.manager_profile.company_name if hasattr(manager, 'manager_profile') else '',
                    "years_of_experience": manager.manager_profile.years_of_experience if hasattr(manager, 'manager_profile') else 0,
                    "specializations": manager.manager_profile.specializations if hasattr(manager, 'manager_profile') else [],
                    "average_rating": float(manager.manager_profile.average_rating) if hasattr(manager, 'manager_profile') else 0,
                    "total_events_managed": manager.manager_profile.total_events_managed if hasattr(manager, 'manager_profile') else 0,
                    "is_verified": manager.manager_profile.is_verified if hasattr(manager, 'manager_profile') else False
                }
            } for manager in page],
            "pagination": {
                "page": page.number,
                "pages": paginator.num_pages,
                "has_next": page.has_next(),
                "has_previous": page.has_previous()
            }
        })

class ManagerDetailView(View):
    def get(self, request, slug):
        try:
            # Try to get by ID first, then by username as slug
            try:
                manager = CustomUser.objects.get(id=slug, user_type='manager')
            except (ValueError, CustomUser.DoesNotExist):
                manager = CustomUser.objects.get(username=slug, user_type='manager')
            
            profile_data = {}
            if hasattr(manager, 'manager_profile'):
                profile = manager.manager_profile
                profile_data = {
                    "company_name": profile.company_name,
                    "job_title": profile.job_title,
                    "years_of_experience": profile.years_of_experience,
                    "specializations": profile.specializations,
                    "certifications": profile.certifications,
                    "awards": profile.awards,
                    "service_areas": profile.service_areas,
                    "travel_radius": profile.travel_radius,
                    "hourly_rate": float(profile.hourly_rate) if profile.hourly_rate else None,
                    "package_pricing": profile.package_pricing,
                    "availability_schedule": profile.availability_schedule,
                    "max_events_per_month": profile.max_events_per_month,
                    "total_events_managed": profile.total_events_managed,
                    "average_rating": float(profile.average_rating),
                    "total_reviews": profile.total_reviews,
                    "is_verified": profile.is_verified,
                    "verification_date": profile.verification_date.isoformat() if profile.verification_date else None
                }
            
            return JsonResponse({
                "success": True,
                "manager": {
                    "id": manager.id,
                    "name": manager.get_full_name(),
                    "email": manager.email,
                    "phone_number": manager.phone_number,
                    "address": {
                        "line1": manager.address_line1,
                        "line2": manager.address_line2,
                        "city": manager.city,
                        "state": manager.state,
                        "postal_code": manager.postal_code,
                        "country": str(manager.country)
                    },
                    "profile_picture": manager.profile_picture.url if manager.profile_picture else None,
                    "social_links": {
                        "facebook": manager.facebook_url,
                        "twitter": manager.twitter_url,
                        "linkedin": manager.linkedin_url,
                        "instagram": manager.instagram_url
                    },
                    "date_joined": manager.date_joined.isoformat(),
                    "is_verified": manager.is_verified,
                    "profile": profile_data,
                    "managed_events": [{
                        "id": event.id,
                        "title": event.title,
                        "start_date": event.start_date.isoformat(),
                        "status": event.status,
                        "venue": event.venue.name if event.venue else None
                    } for event in manager.managed_events.all()[:5]]  # Last 5 events
                }
            })
        except CustomUser.DoesNotExist:
            return JsonResponse({"success": False, "error": "Manager not found"})

class ManagerSpecializationsView(View):
    def get(self, request):
        # Get all unique specializations from manager profiles
        specializations = set()
        profiles = EventManagerProfile.objects.filter(is_verified=True)
        
        for profile in profiles:
            if profile.specializations:
                specializations.update(profile.specializations)
        
        return JsonResponse({
            "success": True,
            "specializations": sorted(list(specializations))
        })

@method_decorator(login_required, name='dispatch')
class ManagerStatsView(View):
    def get(self, request, manager_id):
        try:
            manager = CustomUser.objects.get(id=manager_id, user_type='manager')
            
            # Get manager statistics
            stats = {
                "total_events": manager.managed_events.count(),
                "completed_events": manager.managed_events.filter(status='completed').count(),
                "upcoming_events": manager.managed_events.filter(status='confirmed').count(),
                "total_revenue": sum(event.manager_fee for event in manager.managed_events.filter(status='completed')),
                "client_satisfaction": float(manager.manager_profile.average_rating) if hasattr(manager, 'manager_profile') else 0,
                "repeat_clients": 0  # This would need more complex logic
            }
            
            return JsonResponse({
                "success": True,
                "stats": stats
            })
        except CustomUser.DoesNotExist:
            return JsonResponse({"success": False, "error": "Manager not found"})