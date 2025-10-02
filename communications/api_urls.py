from django.urls import path
from . import api_views

app_name = 'communications_api'

urlpatterns = [
    path('conversations/', api_views.ConversationListView.as_view(), name='conversation_list'),
    path('conversations/<int:pk>/messages/', api_views.MessageListView.as_view(), name='message_list'),
    
    # User search and conversation management
    path('search-users/', api_views.search_users, name='search_users'),
    path('start-conversation/', api_views.start_conversation, name='start_conversation'),
    
    # Advanced chat system endpoints
    path('advanced-chatrooms/', api_views.AdvancedChatRoomCreateView.as_view(), name='advanced_chatroom_create'),
    path('advanced-chatrooms/<int:chatroom_id>/participants/', api_views.AdvancedChatRoomParticipantView.as_view(), name='advanced_chatroom_participants'),
    path('chatrooms/<int:room_id>/available-participants/', api_views.AvailableParticipantsView.as_view(), name='available_participants'),
    path('admins/available/', api_views.AvailableAdminsView.as_view(), name='available_admins'),
    path('managers/available/', api_views.AvailableManagersView.as_view(), name='available_managers'),
    path('chatrooms/<int:room_id>/messages/', api_views.ChatRoomMessagesView.as_view(), name='chatroom_messages'),
    
    # AI Chatbot endpoints
    path('ai-chatbot/response/', api_views.ai_chatbot_response, name='ai_chatbot_response'),
    path('ai-chatbot/analytics/', api_views.ai_chatbot_analytics, name='ai_chatbot_analytics'),
] 