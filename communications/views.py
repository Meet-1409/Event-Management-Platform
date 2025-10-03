from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from users.models import CustomUser
from communications.models import Conversation, Message, ChatRoom, ChatRoomMember, ChatMessage, GroupJoinRequest, AdvancedChatRoom, AdvancedChatRoomParticipant, AdvancedChatMessage
from django.contrib.auth.decorators import login_required
from django.db import models
from django.contrib import messages
from django.urls import reverse
from .forms import GroupChatCreateForm
from django.utils import timezone
from users import role_required

@login_required
def inbox(request):
    """Main inbox view showing all conversations and chat rooms"""
    user = request.user
    
    # Get user's conversations
    conversations = Conversation.objects.filter(
        models.Q(participant1=user) | models.Q(participant2=user)
    ).order_by('-updated_at')
    
    # Get user's chat rooms
    chat_rooms = ChatRoom.objects.filter(members__user=user).order_by('-created_at')
    
    # Get advanced chat rooms
    advanced_rooms = AdvancedChatRoom.objects.filter(participants__user=user).order_by('-created_at')
    
    context = {
        'conversations': conversations,
        'chat_rooms': chat_rooms,
        'advanced_rooms': advanced_rooms,
        'user': user,
    }
    return render(request, 'communications/inbox_simple.html', context)

@login_required
def conversation_list(request):
    """List all conversations for the user"""
    user = request.user
    conversations = Conversation.objects.filter(
        models.Q(participant1=user) | models.Q(participant2=user)
    ).order_by('-updated_at')
    
    context = {
        'conversations': conversations,
        'user': user,
    }
    return render(request, 'communications/conversation_list.html', context)

@login_required
def chat_room(request, conversation_id):
    """Individual chat room view"""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Check if user is part of this conversation
    if request.user not in [conversation.participant1, conversation.participant2]:
        messages.error(request, 'You do not have access to this conversation.')
        return redirect('communications:inbox')
    
    messages_list = conversation.messages.order_by('created_at')
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            conversation.updated_at = timezone.now()
            conversation.save()
            return redirect('communications:chat_room', conversation_id=conversation.id)
    
    context = {
        'conversation': conversation,
        'messages': messages_list,
        'other_user': conversation.participant2 if request.user == conversation.participant1 else conversation.participant1,
    }
    return render(request, 'communications/chat_room.html', context)

@login_required
def start_chat(request, user_id):
    """Start a new conversation with another user"""
    target_user = get_object_or_404(CustomUser, id=user_id)
    
    # Ensure consistent ordering for unique_together
    user1, user2 = (request.user, target_user) if request.user.id < target_user.id else (target_user, request.user)
    
    # Determine conversation_type
    if user1.user_type == 'user' and user2.user_type == 'manager':
        conversation_type = 'user_manager'
    elif user1.user_type == 'manager' and user2.user_type == 'user':
        conversation_type = 'user_manager'
    elif user1.user_type == 'admin' or user2.user_type == 'admin':
        conversation_type = 'admin_user' if 'user' in [user1.user_type, user2.user_type] else 'admin_manager'
    else:
        conversation_type = 'user_manager'
    
    conversation = Conversation.objects.filter(participant1=user1, participant2=user2).first()
    if not conversation:
        conversation = Conversation.objects.create(
            participant1=user1,
            participant2=user2,
            conversation_type=conversation_type
        )
    
    return redirect('communications:chat_room', conversation_id=conversation.id)

@login_required
def advanced_chat_inbox(request):
    """Advanced chat inbox with sample data"""
    user = request.user
    
    # Get existing chatrooms
    chatrooms = AdvancedChatRoom.objects.filter(participants__user=user)
    
    # Create sample chat rooms if none exist (for demo purposes)
    if not chatrooms.exists():
        # Create sample chat rooms
        sample_rooms = [
            {
                'name': 'Pickle Ball Tournament',
                'description': 'Discussion about the upcoming pickle ball tournament'
            },
            {
                'name': 'Soccer Tournament',
                'description': 'Planning for the soccer tournament'
            },
            {
                'name': 'Corporate Event Planning',
                'description': 'Corporate event planning discussion'
            }
        ]
        
        for room_data in sample_rooms:
            room = AdvancedChatRoom.objects.create(
                name=room_data['name'],
                description=room_data['description'],
                created_by=user
            )
            
            # Add current user as participant
            AdvancedChatRoomParticipant.objects.create(
                chatroom=room,
                user=user,
                role='user'
            )
            
            # Add sample message
            AdvancedChatMessage.objects.create(
                chatroom=room,
                sender=user,
                message_content=f"Welcome to {room_data['name']}! The chat room is ready.",
                message_type='system'
            )
        
        # Refresh the queryset
        chatrooms = AdvancedChatRoom.objects.filter(participants__user=user)
    
    context = {
        'chatrooms': chatrooms,
        'user': user,
    }
    return render(request, 'communications/inbox.html', context)

@role_required(['manager', 'admin'])
def create_group(request):
    """Create a new group chat"""
    if request.method == 'POST':
        form = GroupChatCreateForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.save()
            
            # Add creator as member
            ChatRoomMember.objects.create(
                chatroom=group,
                user=request.user,
                role='admin'
            )
            
            messages.success(request, 'Group chat created successfully!')
            return redirect('communications:group_chat_room', room_id=group.id)
    else:
        form = GroupChatCreateForm(current_user=request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'communications/create_group.html', context)

@login_required
def group_chat_room(request, room_id):
    """Group chat room view"""
    room = get_object_or_404(ChatRoom, id=room_id)
    
    # Check if user is member of this room
    if not room.members.filter(user=request.user).exists():
        messages.error(request, 'You do not have access to this group chat.')
        return redirect('communications:inbox')
    
    messages_list = room.messages.order_by('created_at')
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            ChatMessage.objects.create(
                chatroom=room,
                sender=request.user,
                content=content
            )
            return redirect('communications:group_chat_room', room_id=room.id)
    
    context = {
        'room': room,
        'messages': messages_list,
        'members': room.members.all(),
    }
    return render(request, 'communications/group_chat_room.html', context)

@role_required(['manager', 'admin'])
def add_users_to_group(request, room_id):
    """Add users to a group chat"""
    room = get_object_or_404(ChatRoom, id=room_id)
    
    # Check if user is admin of this room
    if not room.members.filter(user=request.user, role='admin').exists():
        messages.error(request, 'You do not have permission to add users to this group.')
        return redirect('communications:inbox')
    
    if request.method == 'POST':
        user_ids = request.POST.getlist('users')
        for user_id in user_ids:
            user = CustomUser.objects.get(id=user_id)
            if not room.members.filter(user=user).exists():
                ChatRoomMember.objects.create(
                    chatroom=room,
                    user=user,
                    role='member'
                )
        
        messages.success(request, 'Users added to group successfully!')
        return redirect('communications:group_chat_room', room_id=room.id)
    
    # Get users not in the group
    existing_members = room.members.values_list('user_id', flat=True)
    available_users = CustomUser.objects.exclude(id__in=existing_members)
    
    context = {
        'room': room,
        'available_users': available_users,
    }
    return render(request, 'communications/add_users_to_group.html', context)

@login_required
def group_join_requests(request):
    """Show join requests for group chats"""
    user = request.user
    
    # Get join requests for groups where user is admin
    admin_rooms = ChatRoom.objects.filter(members__user=user, members__role='admin')
    join_requests = GroupJoinRequest.objects.filter(chatroom__in=admin_rooms, status='pending')
    
    context = {
        'join_requests': join_requests,
        'user': user,
    }
    return render(request, 'communications/group_join_requests.html', context)

@login_required
def handle_join_request(request, request_id, action):
    """Handle group join request (approve/reject)"""
    join_request = get_object_or_404(GroupJoinRequest, id=request_id)
    
    # Check if user is admin of the group
    if not join_request.chatroom.members.filter(user=request.user, role='admin').exists():
        messages.error(request, 'You do not have permission to handle this request.')
        return redirect('communications:group_join_requests')
    
    if action == 'approve':
        join_request.status = 'approved'
        join_request.save()
        
        # Add user to group
        ChatRoomMember.objects.create(
            chatroom=join_request.chatroom,
            user=join_request.user,
            role='member'
        )
        
        messages.success(request, 'Join request approved!')
    elif action == 'reject':
        join_request.status = 'rejected'
        join_request.save()
        messages.success(request, 'Join request rejected!')
    
    return redirect('communications:group_join_requests')
