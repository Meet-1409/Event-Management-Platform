from django.contrib import admin
from .models import (
    Conversation, Message, Consultation, ConsultationNote,
    Notification, NotificationTemplate, ChatRoom, ChatRoomMember, ChatMessage
)

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('conversation_id', 'conversation_type', 'participant1', 'participant2', 'is_active', 'last_message_at')
    list_filter = ('conversation_type', 'is_active', 'is_archived', 'created_at')
    search_fields = ('conversation_id', 'participant1__username', 'participant2__username')
    ordering = ('-last_message_at', '-created_at')
    readonly_fields = ('conversation_id', 'created_at', 'updated_at', 'last_message_at')
    fieldsets = (
        ('Conversation Info', {
            'fields': ('conversation_id', 'conversation_type'),
            'description': 'Basic conversation information.'
        }),
        ('Participants', {
            'fields': ('participant1', 'participant2'),
            'description': 'Users participating in the conversation.'
        }),
        ('Related Objects', {
            'fields': ('event', 'venue', 'vendor'),
            'description': 'Objects related to this conversation.'
        }),
        ('Status', {
            'fields': ('is_active', 'is_archived'),
            'description': 'Conversation status.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_message_at'),
            'description': 'Conversation timeline (read-only).'
        }),
    )

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('message_id', 'conversation', 'sender', 'message_type', 'is_read', 'created_at')
    list_filter = ('message_type', 'is_read', 'is_delivered', 'is_edited', 'is_deleted', 'created_at')
    search_fields = ('message_id', 'sender__username', 'content', 'attachment_name')
    ordering = ('-created_at',)
    readonly_fields = ('message_id', 'created_at', 'updated_at', 'read_at')
    fieldsets = (
        ('Message Info', {
            'fields': ('message_id', 'conversation', 'sender', 'message_type'),
            'description': 'Basic message information.'
        }),
        ('Content', {
            'fields': ('content', 'attachment', 'attachment_name', 'attachment_size'),
            'description': 'Message content and attachments.'
        }),
        ('Status', {
            'fields': ('is_read', 'is_delivered', 'is_edited', 'is_deleted'),
            'description': 'Message delivery and read status.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'read_at'),
            'description': 'Message timeline (read-only).'
        }),
    )

@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('consultation_id', 'user', 'manager', 'consultation_type', 'status', 'scheduled_date', 'is_paid')
    list_filter = ('consultation_type', 'status', 'is_paid', 'created_at')
    search_fields = ('consultation_id', 'user__username', 'manager__username', 'topic')
    ordering = ('-created_at',)
    readonly_fields = ('consultation_id', 'created_at', 'updated_at', 'completed_at')
    fieldsets = (
        ('Consultation Info', {
            'fields': ('consultation_id', 'user', 'manager', 'consultation_type', 'status'),
            'description': 'Basic consultation information.'
        }),
        ('Scheduling', {
            'fields': ('requested_date', 'scheduled_date', 'duration_minutes'),
            'description': 'Consultation scheduling details.'
        }),
        ('Event Context', {
            'fields': ('event', 'event_type', 'expected_guests', 'budget_range'),
            'description': 'Event context for the consultation.'
        }),
        ('Details', {
            'fields': ('topic', 'description', 'specific_questions'),
            'description': 'Consultation topic and questions.'
        }),
        ('Meeting', {
            'fields': ('meeting_link', 'meeting_location', 'meeting_notes'),
            'description': 'Meeting details and notes.'
        }),
        ('Pricing', {
            'fields': ('consultation_fee', 'is_paid'),
            'description': 'Consultation pricing and payment status.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'description': 'Consultation timeline (read-only).'
        }),
    )

@admin.register(ConsultationNote)
class ConsultationNoteAdmin(admin.ModelAdmin):
    list_display = ('consultation', 'author', 'title', 'note_type', 'is_important', 'created_at')
    list_filter = ('note_type', 'is_important', 'is_private', 'created_at')
    search_fields = ('consultation__consultation_id', 'author__username', 'title', 'content')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Note Info', {
            'fields': ('consultation', 'author', 'title', 'note_type'),
            'description': 'Basic note information.'
        }),
        ('Content', {
            'fields': ('content',),
            'description': 'Note content.'
        }),
        ('Visibility', {
            'fields': ('is_private', 'is_important'),
            'description': 'Note visibility and importance settings.'
        }),
    )

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('notification_id', 'user', 'notification_type', 'title', 'priority', 'is_read', 'created_at')
    list_filter = ('notification_type', 'priority', 'is_read', 'is_sent', 'is_delivered', 'created_at')
    search_fields = ('notification_id', 'user__username', 'title', 'message')
    ordering = ('-created_at',)
    readonly_fields = ('notification_id', 'created_at', 'read_at', 'sent_at')
    fieldsets = (
        ('Notification Info', {
            'fields': ('notification_id', 'user', 'notification_type', 'priority'),
            'description': 'Basic notification information.'
        }),
        ('Content', {
            'fields': ('title', 'message', 'action_url', 'action_text'),
            'description': 'Notification content and actions.'
        }),
        ('Related Objects', {
            'fields': ('related_event', 'related_consultation', 'related_conversation'),
            'description': 'Objects related to this notification.'
        }),
        ('Status', {
            'fields': ('is_read', 'is_sent', 'is_delivered'),
            'description': 'Notification delivery status.'
        }),
        ('Delivery Methods', {
            'fields': ('email_sent', 'sms_sent', 'push_sent'),
            'description': 'How the notification was delivered.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'read_at', 'sent_at'),
            'description': 'Notification timeline (read-only).'
        }),
    )

@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'notification_type', 'priority', 'is_active', 'send_email', 'send_sms', 'send_push')
    list_filter = ('notification_type', 'priority', 'is_active', 'send_email', 'send_sms', 'send_push')
    search_fields = ('name', 'title_template', 'message_template')
    ordering = ('name',)
    fieldsets = (
        ('Template Info', {
            'fields': ('name', 'notification_type', 'priority', 'is_active'),
            'description': 'Basic template information.'
        }),
        ('Content', {
            'fields': ('title_template', 'message_template'),
            'description': 'Template content with placeholders.'
        }),
        ('Delivery Settings', {
            'fields': ('send_email', 'send_sms', 'send_push'),
            'description': 'How to deliver this type of notification.'
        }),
    )

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('room_id', 'name', 'chat_type', 'is_private', 'is_active', 'created_at')
    list_filter = ('chat_type', 'is_private', 'is_active', 'created_at')
    search_fields = ('room_id', 'name', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('room_id', 'created_at', 'updated_at')
    fieldsets = (
        ('Room Info', {
            'fields': ('room_id', 'name', 'chat_type'),
            'description': 'Basic room information.'
        }),
        ('Details', {
            'fields': ('description', 'is_private', 'is_active'),
            'description': 'Room details and settings.'
        }),
        ('Related Objects', {
            'fields': ('event',),
            'description': 'Event related to this chat room.'
        }),
    )

@admin.register(ChatRoomMember)
class ChatRoomMemberAdmin(admin.ModelAdmin):
    list_display = ('room', 'user', 'role', 'is_active', 'joined_at', 'last_seen')
    list_filter = ('role', 'is_active', 'joined_at')
    search_fields = ('room__name', 'user__username')
    ordering = ('-joined_at',)
    readonly_fields = ('joined_at', 'last_seen')
    fieldsets = (
        ('Membership Info', {
            'fields': ('room', 'user', 'role'),
            'description': 'Basic membership information.'
        }),
        ('Status', {
            'fields': ('is_active',),
            'description': 'Member status in the room.'
        }),
        ('Activity', {
            'fields': ('joined_at', 'last_seen'),
            'description': 'Member activity timeline (read-only).'
        }),
    )

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('room', 'sender', 'message_type', 'is_edited', 'is_deleted', 'created_at')
    list_filter = ('message_type', 'is_edited', 'is_deleted', 'created_at')
    search_fields = ('room__name', 'sender__username', 'content', 'attachment_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Message Info', {
            'fields': ('room', 'sender', 'message_type'),
            'description': 'Basic message information.'
        }),
        ('Content', {
            'fields': ('content', 'attachment', 'attachment_name'),
            'description': 'Message content and attachments.'
        }),
        ('Status', {
            'fields': ('is_edited', 'is_deleted'),
            'description': 'Message status.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'description': 'Message timeline (read-only).'
        }),
    )
