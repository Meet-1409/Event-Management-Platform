from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from .models import AdvancedChatRoom, AdvancedChatRoomParticipant, AdvancedChatMessage
import json
from django.db import models
from datetime import datetime, timedelta
import re

from events.models import Event, EventType, Registration
from venues.models import Venue
from users.models import CustomUser
from events.utils import get_popular_events, get_recommended_events_for_user

User = get_user_model()

class ConversationListView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)
        
        try:
            # Get conversations where the current user is a participant
            user_conversations = AdvancedChatRoom.objects.filter(
                participants__user=request.user,
                participants__is_visible=True
            ).distinct()
            
            conversations = []
            for conversation in user_conversations:
                # Get the other user in the conversation (not the current user)
                other_participant = conversation.participants.filter(
                    user__user_type='user',
                    is_visible=True
                ).exclude(user=request.user).first()
                
                if other_participant:
                    # Get the last message
                    last_message = conversation.messages.order_by('-sent_at').first()
                    
                    conversations.append({
                        'id': conversation.id,
                        'other_user': {
                            'id': other_participant.user.id,
                            'first_name': other_participant.user.first_name,
                            'last_name': other_participant.user.last_name,
                            'get_full_name': other_participant.user.get_full_name(),
                            'email': other_participant.user.email,
                            'date_joined': other_participant.user.date_joined.strftime('%Y-%m-%d')
                        },
                        'last_message': last_message.message_content if last_message else None,
                        'last_message_time': last_message.sent_at.strftime('%H:%M') if last_message else None,
                        'unread_count': conversation.messages.filter(
                            sender__user_type='user',
                            sent_at__gt=conversation.participants.get(user=request.user).last_read_at or datetime.min
                        ).count() if conversation.participants.filter(user=request.user).exists() else 0
                    })
            
            return JsonResponse({"conversations": conversations})
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

class MessageListView(View):
    def get(self, request, pk):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)
        
        try:
            conversation = get_object_or_404(AdvancedChatRoom, id=pk)
            
            # Check if user is a participant
            if not conversation.participants.filter(user=request.user, is_visible=True).exists():
                return JsonResponse({"error": "Access denied"}, status=403)
            
            # Get messages for this conversation
            messages = conversation.messages.order_by('sent_at')
            
            message_list = []
            for message in messages:
                message_list.append({
                    'id': message.id,
                    'content': message.message_content,
                    'created_at': message.sent_at.strftime('%H:%M'),
                    'is_sent': message.sender == request.user,
                    'sender_name': message.sender.get_full_name() or message.sender.username
                })
            
            # Update last read time for current user
            participant = conversation.participants.get(user=request.user)
            participant.last_read_at = datetime.now()
            participant.save()
            
            return JsonResponse({"messages": message_list})
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    def post(self, request, pk):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)
        
        try:
            data = json.loads(request.body)
            content = data.get('content', '').strip()
            
            if not content:
                return JsonResponse({"error": "Message content is required"}, status=400)
            
            conversation = get_object_or_404(AdvancedChatRoom, id=pk)
            
            # Check if user is a participant
            if not conversation.participants.filter(user=request.user, is_visible=True).exists():
                return JsonResponse({"error": "Access denied"}, status=403)
            
            # Create the message
            message = AdvancedChatMessage.objects.create(
                chatroom=conversation,
                sender=request.user,
                message_content=content
            )
            
            return JsonResponse({
                "success": True,
                "message": {
                    'id': message.id,
                    'content': message.message_content,
                    'created_at': message.sent_at.strftime('%H:%M'),
                    'is_sent': True,
                    'sender_name': message.sender.get_full_name() or message.sender.username
                }
            })
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class AdvancedChatRoomCreateView(View):
    def get(self, request):
        chatrooms = AdvancedChatRoom.objects.all()
        data = [
            {
                'id': room.id,
                'name': room.name or f"ChatRoom {room.id}",
                'created_by': room.created_by.get_full_name() or room.created_by.username,
                'created_at': room.created_at,
            }
            for room in chatrooms
        ]
        return JsonResponse({'chatrooms': data})

    def post(self, request):
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            selected_admin_ids = data.get('selected_admins', [])
            chatroom_name = data.get('chatroom_name', '')
            if not user_id or not selected_admin_ids:
                return JsonResponse({'error': 'user_id and at least one admin required'}, status=400)
            user = get_object_or_404(User, id=user_id)
            chatroom = AdvancedChatRoom.objects.create(name=chatroom_name, created_by=user)
            # Add user as participant
            AdvancedChatRoomParticipant.objects.create(chatroom=chatroom, user=user, role='user', is_visible=True, added_by=user)
            # Add selected admins
            for admin_id in selected_admin_ids:
                admin = get_object_or_404(User, id=admin_id)
                AdvancedChatRoomParticipant.objects.create(chatroom=chatroom, user=admin, role='admin', is_visible=True, added_by=user)
            # Add all superadmins (invisible)
            superadmins = User.objects.filter(user_type='superadmin')
            for sa in superadmins:
                AdvancedChatRoomParticipant.objects.create(chatroom=chatroom, user=sa, role='superadmin', is_visible=False, added_by=None)
            return JsonResponse({'success': True, 'chatroom_id': chatroom.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class AdvancedChatRoomParticipantView(View):
    def post(self, request, chatroom_id):
        try:
            data = json.loads(request.body)
            user_ids = data.get('user_ids', [])
            added_by_id = data.get('added_by')

            if not user_ids or not added_by_id:
                return JsonResponse({'error': 'user_ids and added_by required'}, status=400)

            chatroom = get_object_or_404(AdvancedChatRoom, id=chatroom_id)
            added_by = get_object_or_404(User, id=added_by_id)

            for user_id in user_ids:
                user = get_object_or_404(User, id=user_id)
                
                # Determine role based on who is adding whom
                role = 'participant' # default
                if added_by.user_type == 'user' and user.user_type == 'admin':
                    role = 'admin'
                elif added_by.user_type == 'admin' and user.user_type == 'manager':
                    role = 'manager'
                elif user.user_type == 'user':
                    role = 'user'

                # Prevent duplicates
                if not AdvancedChatRoomParticipant.objects.filter(chatroom=chatroom, user=user).exists():
                    AdvancedChatRoomParticipant.objects.create(
                        chatroom=chatroom, 
                        user=user, 
                        role=role, 
                        is_visible=True, 
                        added_by=added_by
                    )
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def get(self, request, chatroom_id):
        chatroom = get_object_or_404(AdvancedChatRoom, id=chatroom_id)
        participants = AdvancedChatRoomParticipant.objects.filter(chatroom=chatroom)
        data = [
            {
                'user_id': p.user.id,
                'username': p.user.get_full_name() or p.user.username,
                'role': p.role,
                'is_visible': p.is_visible,
                'joined_at': p.joined_at,
            }
            for p in participants
        ]
        return JsonResponse({'participants': data})

class AvailableParticipantsView(View):
    def get(self, request, room_id):
        chatroom = get_object_or_404(AdvancedChatRoom, id=room_id)
        current_user = request.user
        
        # Get existing participant IDs to exclude them
        existing_participant_ids = AdvancedChatRoomParticipant.objects.filter(
            chatroom=chatroom
        ).values_list('user_id', flat=True)

        users_to_add = User.objects.none()
        
        # Regular users can add other users and admins
        if current_user.user_type == 'user':
            users_to_add = User.objects.filter(
                user_type__in=['user', 'admin'], is_active=True
            ).exclude(id__in=existing_participant_ids)
        
        # Admins can add managers
        elif current_user.user_type == 'admin':
            users_to_add = User.objects.filter(
                user_type='manager', is_active=True
            ).exclude(id__in=existing_participant_ids)
            
        data = [
            {'id': user.id, 'username': user.get_full_name() or user.username}
            for user in users_to_add
        ]
        return JsonResponse({'users': data})

class AvailableAdminsView(View):
    def get(self, request):
        admins = User.objects.filter(user_type='admin', is_active=True)
        data = [
            {
                'id': admin.id,
                'username': admin.get_full_name() or admin.username,
                'email': admin.email,
            }
            for admin in admins
        ]
        return JsonResponse({'admins': data})

class AvailableManagersView(View):
    def get(self, request):
        managers = User.objects.filter(user_type='manager', is_active=True)
        data = [
            {
                'id': manager.id,
                'username': manager.get_full_name() or manager.username,
                'email': manager.email,
            }
            for manager in managers
        ]
        return JsonResponse({'managers': data})

class ChatRoomMessagesView(View):
    def get(self, request, room_id):
        room = get_object_or_404(AdvancedChatRoom, id=room_id)
        messages = AdvancedChatMessage.objects.filter(chatroom=room).order_by('sent_at')
        data = [
            {
                'id': msg.id,
                'sender': msg.sender.get_full_name() or msg.sender.username,
                'sender_id': msg.sender.id,
                'content': msg.message_content,
                'sent_at': msg.sent_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for msg in messages
        ]
        return JsonResponse({'messages': data})

    def post(self, request, room_id):
        try:
            room = get_object_or_404(AdvancedChatRoom, id=room_id)
            data = json.loads(request.body)
            message_content = data.get('message', '').strip()
            sender_id = data.get('sender_id')
            
            if not message_content or not sender_id:
                return JsonResponse({'error': 'Message and sender_id are required'}, status=400)
            
            sender = get_object_or_404(User, id=sender_id)
            
            # Check if user is a participant
            if not room.participants.filter(user=sender).exists():
                return JsonResponse({'error': 'User is not a participant in this room'}, status=403)
            
            # Save message
            chat_message = AdvancedChatMessage.objects.create(
                chatroom=room,
                sender=sender,
                message_content=message_content,
                message_type='text'
            )
            
            return JsonResponse({
                'success': True,
                'message': {
                    'id': chat_message.id,
                    'sender': sender.get_full_name() or sender.username,
                    'sender_id': sender.id,
                    'content': chat_message.message_content,
                    'sent_at': chat_message.sent_at.strftime('%Y-%m-%d %H:%M:%S'),
                }
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500) 

@csrf_exempt
@require_http_methods(["GET"])
def search_users(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)
    
    try:
        query = request.GET.get('q', '').strip()
        if len(query) < 2:
            return JsonResponse({"users": []})
        
        # Search users by name or email
        users = User.objects.filter(
            models.Q(first_name__icontains=query) |
            models.Q(last_name__icontains=query) |
            models.Q(email__icontains=query) |
            models.Q(username__icontains=query)
        ).exclude(id=request.user.id)[:10]
        
        user_list = []
        for user in users:
            user_list.append({
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'get_full_name': user.get_full_name(),
                'email': user.email,
                'username': user.username
            })
        
        return JsonResponse({"users": user_list})
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def start_conversation(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)
    
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        
        if not user_id:
            return JsonResponse({"error": "user_id is required"}, status=400)
        
        other_user = get_object_or_404(User, id=user_id)
        
        # Check if conversation already exists
        existing_conversation = AdvancedChatRoom.objects.filter(
            participants__user=request.user,
            participants__is_visible=True
        ).filter(
            participants__user=other_user,
            participants__is_visible=True
        ).first()
        
        if existing_conversation:
            return JsonResponse({
                "success": True,
                "conversation_id": existing_conversation.id,
                "message": "Conversation already exists"
            })
        
        # Create new conversation
        conversation = AdvancedChatRoom.objects.create(
            name=f"Chat between {request.user.get_full_name()} and {other_user.get_full_name()}",
            created_by=request.user
        )
        
        # Add both users as participants
        AdvancedChatRoomParticipant.objects.create(
            chatroom=conversation,
            user=request.user,
            role='user',
            is_visible=True,
            added_by=request.user
        )
        
        AdvancedChatRoomParticipant.objects.create(
            chatroom=conversation,
            user=other_user,
            role='user',
            is_visible=True,
            added_by=request.user
        )
        
        return JsonResponse({
            "success": True,
            "conversation_id": conversation.id,
            "message": "Conversation created successfully"
        })
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def ai_chatbot_response(request):
    """AI Chatbot endpoint for intelligent responses"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').lower()
        user_id = data.get('user_id')
        
        # Get user if authenticated
        user = None
        if user_id:
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                pass
        
        # Process the message and generate response
        response = process_ai_message(user_message, user)
        
        return JsonResponse({
            'success': True,
            'response': response['message'],
            'action': response.get('action'),
            'data': response.get('data', {})
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def process_ai_message(message, user=None):
    """Process user message and generate intelligent response"""
    
    message_lower = message.lower()
    
    # Check for specific event types first (more specific queries)
    if any(word in message_lower for word in ['pickleball', 'tennis', 'badminton', 'volleyball', 'basketball', 'cricket', 'football', 'soccer', 'golf', 'swimming', 'yoga', 'fitness', 'gym']):
        return handle_sports_query(message, user)
    
    elif any(word in message_lower for word in ['music', 'concert', 'festival', 'band', 'dj', 'karaoke', 'dance']):
        return handle_music_query(message, user)
    
    elif any(word in message_lower for word in ['tech', 'conference', 'workshop', 'coding', 'programming', 'webinar', 'seminar', 'training']):
        return handle_tech_query(message, user)
    
    elif any(word in message_lower for word in ['wedding', 'birthday', 'party', 'celebration', 'anniversary', 'corporate', 'meeting']):
        return handle_event_query(message, user)
    
    # Booking-related queries
    elif any(word in message_lower for word in ['book', 'booking', 'register', 'registration', 'how to', 'process', 'steps']):
        return handle_booking_query(message, user)
    
    # Venue-related queries
    elif any(word in message_lower for word in ['venue', 'venues', 'location', 'place', 'where', 'hall', 'room', 'facility']):
        return handle_venue_query(message, user)
    
    # Pricing queries
    elif any(word in message_lower for word in ['price', 'cost', 'fee', 'payment', 'money', 'budget', 'expensive', 'cheap']):
        return handle_pricing_query(message, user)
    
    # General event-related queries
    elif any(word in message_lower for word in ['event', 'events', 'upcoming', 'available', 'happening', 'show', 'find', 'search']):
        return handle_event_query(message, user)
    
    # Help queries
    elif any(word in message_lower for word in ['help', 'support', 'assist', 'what can you do', 'capabilities']):
        return handle_help_query(message, user)
    
    # Default response
    else:
        return handle_general_query(message, user)

def handle_event_query(message, user):
    """Handle event-related queries"""
    try:
        message_lower = message.lower()
        
        # Check for specific keywords in the message
        if any(word in message_lower for word in ['tomorrow', 'today', 'this week', 'next week']):
            # Handle time-specific queries
            if 'tomorrow' in message_lower:
                target_date = datetime.now().date() + timedelta(days=1)
                events = Event.objects.filter(
                    start_date=target_date,
                    status='confirmed'
                ).order_by('start_time')
            elif 'today' in message_lower:
                target_date = datetime.now().date()
                events = Event.objects.filter(
                    start_date=target_date,
                    status='confirmed'
                ).order_by('start_time')
            else:
                # This week or next week
                start_date = datetime.now().date()
                end_date = start_date + timedelta(days=7)
                events = Event.objects.filter(
                    start_date__gte=start_date,
                    start_date__lte=end_date,
                    status='confirmed'
                ).order_by('start_date', 'start_time')
        else:
            # General upcoming events
            events = Event.objects.filter(
                start_date__gte=datetime.now().date(),
                status='confirmed'
            ).order_by('start_date', 'start_time')[:5]
        
        if events.exists():
            event_list = []
            for event in events:
                event_list.append(f"🎪 **{event.title}**\n📅 {event.start_date.strftime('%B %d, %Y')}\n🕒 {event.start_time.strftime('%I:%M %p') if event.start_time else 'TBD'}\n📍 {event.venue.name if event.venue else 'TBD'}\n💰 ₹{event.total_cost:,}")
            
            if 'tomorrow' in message_lower:
                response_text = "Here are the events happening tomorrow:\n\n" + "\n\n".join(event_list)
            elif 'today' in message_lower:
                response_text = "Here are the events happening today:\n\n" + "\n\n".join(event_list)
            else:
                response_text = "Here are some exciting upcoming events:\n\n" + "\n\n".join(event_list)
            
            response_text += "\n\nWould you like me to show you more details about any of these events?"
            
            return {
                'message': response_text,
                'action': 'show_events_list',
                'data': {
                    'events_count': events.count(),
                    'events': list(events.values('id', 'title', 'start_date', 'start_time', 'total_cost'))
                }
            }
        else:
            if 'tomorrow' in message_lower:
                return {
                    'message': "I don't see any events scheduled for tomorrow. Would you like me to show you events for the rest of the week or help you create an event?",
                    'action': 'no_events_tomorrow'
                }
            elif 'today' in message_lower:
                return {
                    'message': "I don't see any events scheduled for today. Would you like me to show you upcoming events or help you create an event?",
                    'action': 'no_events_today'
                }
            else:
                return {
                    'message': "I don't see any upcoming events at the moment. Would you like me to help you create an event or check our event calendar?",
                    'action': 'no_events'
                }
            
    except Exception as e:
        return {
            'message': "I'm having trouble accessing the events right now. Please try again later or contact our support team.",
            'action': 'error'
        }

def handle_booking_query(message, user):
    """Handle booking-related queries"""
    booking_steps = [
        "1️⃣ **Browse Events** - Visit our events page to see all available events",
        "2️⃣ **Select Event** - Choose your preferred event and click 'Book Now'",
        "3️⃣ **Fill Details** - Provide your contact information and preferences",
        "4️⃣ **Review & Pay** - Review your booking details and make secure payment",
        "5️⃣ **Confirmation** - Receive instant booking confirmation via email"
    ]
    
    response_text = "Booking an event is super easy! Here's the step-by-step process:\n\n" + "\n\n".join(booking_steps)
    response_text += "\n\nI can help you with any specific step. What would you like to know?"
    
    return {
        'message': response_text,
        'action': 'show_booking_guide'
    }

def handle_venue_query(message, user):
    """Handle venue-related queries"""
    try:
        # Get popular venues
        popular_venues = Venue.objects.filter(
            is_available=True
        ).order_by('-rating')[:5]
        
        if popular_venues.exists():
            venue_list = []
            for venue in popular_venues:
                venue_list.append(f"🏢 **{venue.name}**\n📍 {venue.city}, {venue.state}\n💰 Starting from ₹{venue.base_price:,}\n⭐ Rating: {venue.rating}/5")
            
            response_text = "Here are some popular venues in your area:\n\n" + "\n\n".join(venue_list)
            response_text += "\n\nWould you like me to show you more venues or help you book one?"
            
            return {
                'message': response_text,
                'action': 'show_venues_list',
                'data': {
                    'venues_count': popular_venues.count(),
                    'venues': list(popular_venues.values('id', 'name', 'city', 'base_price', 'rating'))
                }
            }
        else:
            return {
                'message': "I don't see any venues available at the moment. Would you like me to help you find alternative options?",
                'action': 'no_venues'
            }
            
    except Exception as e:
        return {
            'message': "I'm having trouble accessing venue information right now. Please try again later.",
            'action': 'error'
        }

def handle_pricing_query(message, user):
    """Handle pricing-related queries"""
    try:
        # Get pricing statistics
        events = Event.objects.filter(status='confirmed')
        if events.exists():
            min_price = events.aggregate(min_price=models.Min('total_cost'))['min_price']
            max_price = events.aggregate(max_price=models.Max('total_cost'))['max_price']
            avg_price = events.aggregate(avg_price=models.Avg('total_cost'))['avg_price']
            
            response_text = f"Our pricing varies based on event type and venue:\n\n"
            response_text += f"💰 **Basic Events** - Starting from ₹{min_price:,}\n"
            response_text += f"💰 **Standard Events** - Average ₹{avg_price:,.0f}\n"
            response_text += f"💰 **Premium Events** - Up to ₹{max_price:,}\n\n"
            response_text += "We also offer special discounts for:\n"
            response_text += "• Early bookings (10% off)\n"
            response_text += "• Group bookings (15% off)\n"
            response_text += "• Corporate clients (20% off)\n\n"
            response_text += "Would you like me to help you find the best option for your budget?"
            
            return {
                'message': response_text,
                'action': 'show_pricing',
                'data': {
                    'min_price': min_price,
                    'max_price': max_price,
                    'avg_price': avg_price
                }
            }
        else:
            return {
                'message': "Our pricing varies based on event type and venue. Would you like me to help you get a custom quote?",
                'action': 'custom_quote'
            }
            
    except Exception as e:
        return {
            'message': "I can help you with pricing information. Our events typically range from ₹5,000 to ₹1,00,000 depending on the type and venue. Would you like a specific quote?",
            'action': 'pricing_info'
        }

def handle_sports_query(message, user):
    """Handle sports-related queries"""
    try:
        message_lower = message.lower()
        
        # Define sports keywords and their search terms
        sports_keywords = {
            'pickleball': ['pickleball', 'pickle ball'],
            'tennis': ['tennis'],
            'badminton': ['badminton'],
            'volleyball': ['volleyball', 'volley ball'],
            'basketball': ['basketball', 'basket ball'],
            'cricket': ['cricket'],
            'football': ['football', 'soccer'],
            'golf': ['golf'],
            'swimming': ['swimming', 'swim'],
            'yoga': ['yoga'],
            'fitness': ['fitness', 'gym', 'workout', 'exercise']
        }
        
        # Find which sport is being asked about
        requested_sport = None
        for sport, keywords in sports_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                requested_sport = sport
                break
        
        if requested_sport:
            # Search for events with the specific sport
            from django.db.models import Q
            
            # Create search query for the specific sport
            sport_queries = sports_keywords[requested_sport]
            query = Q()
            for keyword in sport_queries:
                query |= Q(title__icontains=keyword) | Q(description__icontains=keyword)
            
            sports_events = Event.objects.filter(
                query,
                start_date__gte=datetime.now().date(),
                status='confirmed'
            ).order_by('start_date')[:5]
            
            if sports_events.exists():
                event_list = []
                for event in sports_events:
                    event_list.append(f"🏓 **{event.title}**\n📅 {event.start_date.strftime('%B %d, %Y')}\n🕒 {event.start_time.strftime('%I:%M %p') if event.start_time else 'TBD'}\n📍 {event.venue.name if event.venue else 'TBD'}\n💰 ₹{event.total_cost:,}")
                
                response_text = f"Here are some exciting {requested_sport.title()} events:\n\n" + "\n\n".join(event_list)
                response_text += f"\n\nWould you like to register for any of these {requested_sport} events?"
                
                return {
                    'message': response_text,
                    'action': 'show_sports_events',
                    'data': {
                        'sport': requested_sport,
                        'events': list(sports_events.values('id', 'title', 'start_date', 'start_time', 'total_cost'))
                    }
                }
            else:
                # No specific events found, provide a helpful response
                sport_emojis = {
                    'pickleball': '🏓', 'tennis': '🎾', 'badminton': '🏸', 'volleyball': '🏐',
                    'basketball': '🏀', 'cricket': '🏏', 'football': '⚽', 'golf': '⛳',
                    'swimming': '🏊', 'yoga': '🧘', 'fitness': '💪'
                }
                
                emoji = sport_emojis.get(requested_sport, '🏓')
                return {
                    'message': f"{emoji} I don't see any specific {requested_sport} events scheduled at the moment. However, I can help you:\n\n"
                              f"• Search for other sports events\n"
                              f"• Help you create a {requested_sport} event\n"
                              f"• Find venues that host {requested_sport} events\n"
                              f"• Check our upcoming sports calendar\n\n"
                              f"What would you like to do?",
                    'action': 'no_specific_sport_events'
                }
        
        # If no specific sport found, show general sports events
        sports_events = Event.objects.filter(
            Q(title__icontains='sport') | 
            Q(title__icontains='football') | 
            Q(title__icontains='soccer') |
            Q(event_type__name__icontains='sport'),
            start_date__gte=datetime.now().date(),
            status='confirmed'
        ).order_by('start_date')[:3]
        
        if sports_events.exists():
            event_list = []
            for event in sports_events:
                event_list.append(f"⚽ **{event.title}**\n📅 {event.start_date.strftime('%B %d, %Y')}\n🕒 {event.start_time.strftime('%I:%M %p') if event.start_time else 'TBD'}\n📍 {event.venue.name if event.venue else 'TBD'}\n💰 ₹{event.total_cost:,}")
            
            response_text = "Here are some exciting sports events:\n\n" + "\n\n".join(event_list)
            response_text += "\n\nWould you like to register for any of these events?"
            
            return {
                'message': response_text,
                'action': 'show_sports_events',
                'data': {
                    'events': list(sports_events.values('id', 'title', 'start_date', 'start_time', 'total_cost'))
                }
            }
        else:
            return {
                'message': "⚽ **Football Tournament 2024**\n\n📅 **Date**: January 25, 2025\n🕒 **Time**: 3:00 PM - 6:00 PM\n📍 **Location**: City Sports Complex\n💰 **Entry Fee**: ₹500 per team\n🏆 **Prize Pool**: ₹10,000\n👥 **Team Size**: 5 players\n\nWould you like to register?",
                'action': 'show_football_details'
            }
            
    except Exception as e:
        return {
            'message': "I'm having trouble accessing the sports events right now. Please try again later or contact our support team.",
            'action': 'error'
        }

def handle_music_query(message, user):
    """Handle music-related queries"""
    try:
        music_events = Event.objects.filter(
            Q(title__icontains='music') | 
            Q(title__icontains='concert') | 
            Q(title__icontains='festival') |
            Q(event_type__name__icontains='entertainment'),
            start_date__gte=datetime.now().date(),
            status='confirmed'
        ).order_by('start_date')[:3]
        
        if music_events.exists():
            event_list = []
            for event in music_events:
                event_list.append(f"🎵 **{event.title}**\n📅 {event.start_date.strftime('%B %d, %Y')}\n🕒 {event.start_time.strftime('%I:%M %p')}\n📍 {event.venue.name if event.venue else 'TBD'}\n💰 ₹{event.total_cost:,}")
            
            response_text = "Here are some amazing music events:\n\n" + "\n\n".join(event_list)
            response_text += "\n\nWould you like to book tickets for any of these events?"
            
            return {
                'message': response_text,
                'action': 'show_music_events',
                'data': {
                    'events': list(music_events.values('id', 'title', 'start_date', 'start_time', 'total_cost'))
                }
            }
        else:
            return {
                'message': "🎵 **Music Festival 2025**\n\n📅 **Date**: January 20, 2025\n🕒 **Time**: 6:00 PM - 11:00 PM\n📍 **Location**: City Park, Ahmedabad\n💰 **Ticket Price**: ₹1,500\n🎤 **Featured Artists**: 5+ local bands\n🍔 **Food & Drinks**: Available on site\n\nWould you like to book tickets?",
                'action': 'show_music_details'
            }
            
    except Exception as e:
        return {
            'message': "🎵 **Music Festival 2025**\n\n📅 **Date**: January 20, 2025\n🕒 **Time**: 6:00 PM - 11:00 PM\n📍 **Location**: City Park, Ahmedabad\n💰 **Ticket Price**: ₹1,500\n🎤 **Featured Artists**: 5+ local bands\n🍔 **Food & Drinks**: Available on site\n\nWould you like to book tickets?",
            'action': 'show_music_details'
        }

def handle_tech_query(message, user):
    """Handle tech-related queries"""
    try:
        tech_events = Event.objects.filter(
            Q(title__icontains='tech') | 
            Q(title__icontains='conference') | 
            Q(title__icontains='workshop') |
            Q(event_type__name__icontains='technology'),
            start_date__gte=datetime.now().date(),
            status='confirmed'
        ).order_by('start_date')[:3]
        
        if tech_events.exists():
            event_list = []
            for event in tech_events:
                event_list.append(f"💻 **{event.title}**\n📅 {event.start_date.strftime('%B %d, %Y')}\n🕒 {event.start_time.strftime('%I:%M %p')}\n📍 {event.venue.name if event.venue else 'TBD'}\n💰 ₹{event.total_cost:,}")
            
            response_text = "Here are some exciting tech events:\n\n" + "\n\n".join(event_list)
            response_text += "\n\nWould you like to register for any of these events?"
            
            return {
                'message': response_text,
                'action': 'show_tech_events',
                'data': {
                    'events': list(tech_events.values('id', 'title', 'start_date', 'start_time', 'total_cost'))
                }
            }
        else:
            return {
                'message': "💻 **Tech Conference 2024**\n\n📅 **Date**: January 15, 2025\n🕒 **Time**: 9:00 AM - 5:00 PM\n📍 **Location**: Convention Center\n💰 **Ticket Price**: ₹250\n🎤 **Speakers**: 10+ industry experts\n📚 **Topics**: AI, Web3, Cloud Computing\n☕ **Includes**: Lunch & coffee breaks\n\nWould you like to register?",
                'action': 'show_tech_details'
            }
            
    except Exception as e:
        return {
            'message': "💻 **Tech Conference 2024**\n\n📅 **Date**: January 15, 2025\n🕒 **Time**: 9:00 AM - 5:00 PM\n📍 **Location**: Convention Center\n💰 **Ticket Price**: ₹2,500\n🎤 **Speakers**: 10+ industry experts\n📚 **Topics**: AI, Web3, Cloud Computing\n☕ **Includes**: Lunch & coffee breaks\n\nWould you like to register?",
            'action': 'show_tech_details'
        }

def handle_help_query(message, user):
    """Handle help-related queries"""
    help_text = "I'm your 360° Event Assistant! Here's what I can help you with:\n\n"
    help_text += "🎯 **Find Events** - Browse upcoming events and get details\n"
    help_text += "📅 **Book Events** - Help with the booking process\n"
    help_text += "🏢 **Find Venues** - Discover perfect venues for your events\n"
    help_text += "💰 **Pricing Info** - Get cost estimates and package options\n"
    help_text += "🎪 **Event Planning** - Get tips and guidance for event planning\n"
    help_text += "📞 **Support** - Connect with our customer support team\n\n"
    help_text += "What would you like to know more about?"
    
    return {
        'message': help_text,
        'action': 'general_help'
    }

def handle_general_query(message, user):
    """Handle general queries"""
    general_responses = [
        "I'm here to help you with everything related to events! You can ask me about upcoming events, booking processes, venues, pricing, or any other event-related questions.",
        "I'm your 360° Event Assistant! I can help you find events, book venues, get pricing information, and much more. What would you like to know?",
        "Welcome! I'm here to make your event planning experience amazing. I can help you discover events, find venues, and answer any questions you have.",
        "Hi there! I'm your personal event assistant. I can help you with event bookings, venue selection, pricing information, and more. What can I help you with today?"
    ]
    
    import random
    response_text = random.choice(general_responses)
    
    return {
        'message': response_text,
        'action': 'general_help'
    }

@csrf_exempt
@require_http_methods(["POST"])
def ai_chatbot_analytics(request):
    """Track chatbot usage analytics"""
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        message = data.get('message', '')
        response_type = data.get('response_type', '')
        
        # Here you could save analytics data to track chatbot usage
        # For now, we'll just return success
        
        return JsonResponse({
            'success': True,
            'message': 'Analytics tracked successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500) 