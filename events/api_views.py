from django.http import JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from .models import Event, EventType, Registration
from django.views.decorators.csrf import csrf_exempt
import json

class EventListView(View):
    def get(self, request):
        events = Event.objects.filter(is_public=True).order_by('-created_at')
        
        # Filtering
        event_type = request.GET.get('type')
        if event_type:
            events = events.filter(event_type__name__icontains=event_type)
            
        paginator = Paginator(events, 20)
        page = paginator.get_page(request.GET.get('page', 1))
        
        return JsonResponse({
            "success": True,
            "events": [{
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "event_type": event.event_type.name,
                "start_date": event.start_date.isoformat(),
                "start_time": event.start_time.strftime('%H:%M'),
                "venue": event.venue.name if event.venue else None,
                "expected_guests": event.expected_guests,
                "total_cost": float(event.total_cost),
                "status": event.status,
                "is_upcoming": event.is_upcoming
            } for event in page],
            "pagination": {
                "page": page.number,
                "pages": paginator.num_pages,
                "has_next": page.has_next(),
                "has_previous": page.has_previous()
            }
        })

class EventDetailView(View):
    def get(self, request, pk):
        try:
            event = Event.objects.get(id=pk)
            return JsonResponse({
                "success": True,
                "event": {
                    "id": event.id,
                    "title": event.title,
                    "description": event.description,
                    "event_type": event.event_type.name,
                    "start_date": event.start_date.isoformat(),
                    "end_date": event.end_date.isoformat(),
                    "start_time": event.start_time.strftime('%H:%M'),
                    "end_time": event.end_time.strftime('%H:%M'),
                    "venue": {
                        "id": event.venue.id,
                        "name": event.venue.name,
                        "address": event.venue.address
                    } if event.venue else None,
                    "expected_guests": event.expected_guests,
                    "total_cost": float(event.total_cost),
                    "venue_cost": float(event.venue_cost),
                    "status": event.status,
                    "organizer": event.organizer.get_full_name(),
                    "created_at": event.created_at.isoformat(),
                    "is_upcoming": event.is_upcoming,
                    "is_ongoing": event.is_ongoing
                }
            })
        except Event.DoesNotExist:
            return JsonResponse({"success": False, "error": "Event not found"})

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class EventRegistrationView(View):
    def post(self, request, event_id):
        try:
            event = Event.objects.get(id=event_id)
            data = json.loads(request.body)
            
            registration = Registration.objects.create(
                event=event,
                name=data.get('name', request.user.get_full_name()),
                email=data.get('email', request.user.email),
                phone=data.get('phone', request.user.phone_number or '')
            )
            
            return JsonResponse({
                "success": True,
                "message": "Registration successful",
                "registration_id": registration.id
            })
        except Event.DoesNotExist:
            return JsonResponse({"success": False, "error": "Event not found"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

class EventTypesView(View):
    def get(self, request):
        event_types = EventType.objects.filter(is_active=True)
        return JsonResponse({
            "success": True,
            "event_types": [{
                "id": et.id,
                "name": et.name,
                "description": et.description,
                "icon": et.icon,
                "color": et.color
            } for et in event_types]
        })

@method_decorator(login_required, name='dispatch')
class MyEventsView(View):
    def get(self, request):
        events = Event.objects.filter(organizer=request.user).order_by('-created_at')
        return JsonResponse({
            "success": True,
            "events": [{
                "id": event.id,
                "title": event.title,
                "start_date": event.start_date.isoformat(),
                "status": event.status,
                "total_cost": float(event.total_cost),
                "venue": event.venue.name if event.venue else None
            } for event in events]
        })

@method_decorator(login_required, name='dispatch')
class MyRegistrationsView(View):
    def get(self, request):
        registrations = Registration.objects.filter(email=request.user.email).order_by('-created_at')
        return JsonResponse({
            "success": True,
            "registrations": [{
                "id": reg.id,
                "event": {
                    "id": reg.event.id,
                    "title": reg.event.title,
                    "start_date": reg.event.start_date.isoformat(),
                    "venue": reg.event.venue.name if reg.event.venue else None
                },
                "registered_at": reg.created_at.isoformat()
            } for reg in registrations]
        })