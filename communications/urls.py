from django.urls import path
from . import views

app_name = 'communications'

urlpatterns = [
    # Main inbox and conversation views
    path('', views.inbox, name='inbox'),
    path('inbox/', views.inbox, name='inbox_detail'),
    path('conversations/', views.conversation_list, name='conversation_list'),
    path('chat/<int:conversation_id>/', views.chat_room, name='chat_room'),
    path('start_chat/<int:user_id>/', views.start_chat, name='start_chat'),
    
    # Advanced chat system
    path('advanced-inbox/', views.advanced_chat_inbox, name='advanced_inbox'),
    
    # Group chat functionality
    path('create-group/', views.create_group, name='create_group'),
    path('group/<int:room_id>/', views.group_chat_room, name='group_chat_room'),
    path('group/<int:room_id>/add-users/', views.add_users_to_group, name='add_users_to_group'),
    path('group-join-requests/', views.group_join_requests, name='group_join_requests'),
    path('group-join-request/<int:request_id>/<str:action>/', views.handle_join_request, name='handle_join_request'),
] 