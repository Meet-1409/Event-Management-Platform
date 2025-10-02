from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
from django.conf import settings


class Conversation(models.Model):
    """
    Conversation between users for messaging
    """
    CONVERSATION_TYPE_CHOICES = [
        ('user_manager', 'User-Manager'),
        ('user_vendor', 'User-Vendor'),
        ('manager_vendor', 'Manager-Vendor'),
        ('admin_user', 'Admin-User'),
        ('admin_manager', 'Admin-Manager'),
        ('admin_vendor', 'Admin-Vendor'),
    ]
    
    # Basic information
    conversation_id = models.CharField(max_length=50, unique=True, blank=True)
    conversation_type = models.CharField(max_length=20, choices=CONVERSATION_TYPE_CHOICES)
    
    # Participants
    participant1 = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='conversations_as_participant1')
    participant2 = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='conversations_as_participant2')
    
    # Related objects
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='conversations', null=True, blank=True)
    venue = models.ForeignKey('venues.Venue', on_delete=models.CASCADE, related_name='conversations', null=True, blank=True)
    vendor = models.ForeignKey('vendors.Vendor', on_delete=models.CASCADE, related_name='conversations', null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'conversations'
        ordering = ['-last_message_at', '-created_at']
        unique_together = ['participant1', 'participant2', 'event']
    
    def __str__(self):
        return f"Conversation {self.conversation_id} - {self.participant1.get_full_name()} & {self.participant2.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.conversation_id:
            self.conversation_id = f"CONV{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def participants(self):
        return [self.participant1, self.participant2]
    
    @property
    def unread_count_for_user(self, user):
        return self.messages.filter(is_read=False).exclude(sender=user).count()


class Message(models.Model):
    """
    Individual messages in conversations
    """
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
        ('system', 'System'),
        ('notification', 'Notification'),
    ]
    
    # Basic information
    message_id = models.CharField(max_length=50, unique=True, blank=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='sent_messages')
    
    # Message content
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text')
    content = models.TextField()
    
    # Media attachments
    attachment = models.FileField(upload_to='message_attachments/', blank=True, null=True)
    attachment_name = models.CharField(max_length=255, blank=True)
    attachment_size = models.PositiveIntegerField(null=True, blank=True)
    
    # Message status
    is_read = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender.get_full_name()} - {self.content[:50]}"
    
    def save(self, *args, **kwargs):
        if not self.message_id:
            self.message_id = f"MSG{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class Consultation(models.Model):
    """
    Consultation requests and scheduling
    """
    CONSULTATION_STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    CONSULTATION_TYPE_CHOICES = [
        ('phone', 'Phone Call'),
        ('video', 'Video Call'),
        ('in_person', 'In Person'),
        ('chat', 'Chat'),
        ('email', 'Email'),
    ]
    
    # Basic information
    consultation_id = models.CharField(max_length=50, unique=True, blank=True)
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='requested_consultations')
    manager = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='managed_consultations')
    
    # Consultation details
    consultation_type = models.CharField(max_length=20, choices=CONSULTATION_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=CONSULTATION_STATUS_CHOICES, default='requested')
    
    # Scheduling
    requested_date = models.DateTimeField()
    scheduled_date = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=30)
    
    # Event context
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='consultations', null=True, blank=True)
    event_type = models.CharField(max_length=100, blank=True)
    expected_guests = models.PositiveIntegerField(null=True, blank=True)
    budget_range = models.CharField(max_length=50, blank=True)
    
    # Consultation details
    topic = models.CharField(max_length=200)
    description = models.TextField()
    specific_questions = models.TextField(blank=True)
    
    # Meeting details
    meeting_link = models.URLField(blank=True)
    meeting_location = models.CharField(max_length=255, blank=True)
    meeting_notes = models.TextField(blank=True)
    
    # Pricing
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'consultations'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Consultation {self.consultation_id} - {self.user.get_full_name()} with {self.manager.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.consultation_id:
            self.consultation_id = f"CONS{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def is_upcoming(self):
        from django.utils import timezone
        return self.scheduled_date and self.scheduled_date > timezone.now()
    
    @property
    def is_overdue(self):
        from django.utils import timezone
        return self.scheduled_date and self.scheduled_date < timezone.now() and self.status in ['scheduled', 'confirmed']


class ConsultationNote(models.Model):
    """
    Notes taken during consultations
    """
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='consultation_notes')
    
    # Note content
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    note_type = models.CharField(max_length=20, choices=[
        ('general', 'General'),
        ('action_items', 'Action Items'),
        ('follow_up', 'Follow Up'),
        ('recommendations', 'Recommendations'),
        ('budget', 'Budget'),
        ('timeline', 'Timeline'),
    ], default='general')
    
    # Visibility
    is_private = models.BooleanField(default=False)
    is_important = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'consultation_notes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Note by {self.author.get_full_name()} - {self.consultation.consultation_id}"


class Notification(models.Model):
    """
    System notifications for users
    """
    NOTIFICATION_TYPE_CHOICES = [
        ('message', 'New Message'),
        ('consultation', 'Consultation Update'),
        ('event', 'Event Update'),
        ('payment', 'Payment Update'),
        ('booking', 'Booking Update'),
        ('system', 'System Notification'),
        ('reminder', 'Reminder'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Basic information
    notification_id = models.CharField(max_length=50, unique=True, blank=True)
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='notifications')
    
    # Notification details
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Related objects
    related_event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    related_consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    related_conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    
    # Action data
    action_url = models.URLField(blank=True)
    action_text = models.CharField(max_length=100, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)
    
    # Delivery methods
    email_sent = models.BooleanField(default=False)
    sms_sent = models.BooleanField(default=False)
    push_sent = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.user.get_full_name()} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.notification_id:
            self.notification_id = f"NOTIF{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class NotificationTemplate(models.Model):
    """
    Templates for system notifications
    """
    name = models.CharField(max_length=100, unique=True)
    notification_type = models.CharField(max_length=20, choices=Notification.NOTIFICATION_TYPE_CHOICES)
    
    # Template content
    title_template = models.CharField(max_length=200)
    message_template = models.TextField()
    
    # Delivery settings
    send_email = models.BooleanField(default=True)
    send_sms = models.BooleanField(default=False)
    send_push = models.BooleanField(default=True)
    
    # Priority
    priority = models.CharField(max_length=10, choices=Notification.PRIORITY_CHOICES, default='medium')
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_templates'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ChatRoom(models.Model):
    """
    Real-time chat rooms for group discussions
    """
    CHAT_TYPE_CHOICES = [
        ('event', 'Event Chat'),
        ('team', 'Team Chat'),
        ('support', 'Support Chat'),
        ('general', 'General Chat'),
    ]
    
    # Basic information
    room_id = models.CharField(max_length=50, unique=True, blank=True)
    name = models.CharField(max_length=200)
    chat_type = models.CharField(max_length=20, choices=CHAT_TYPE_CHOICES)
    
    # Room details
    description = models.TextField(blank=True)
    is_private = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Related objects
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='chat_rooms', null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_rooms'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Chat Room: {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.room_id:
            self.room_id = f"ROOM{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class ChatRoomMember(models.Model):
    """
    Members of chat rooms
    """
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    ]
    
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='chat_room_memberships')
    
    # Member details
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    joined_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    last_read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'chat_room_members'
        unique_together = ['room', 'user']
    
    def __str__(self):
        return f"{self.user.get_full_name()} in {self.room.name}"


class ChatMessage(models.Model):
    """
    Messages in chat rooms
    """
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
        ('system', 'System'),
    ]
    
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='chat_messages')
    
    # Message content
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text')
    content = models.TextField()
    
    # Media attachments
    attachment = models.FileField(upload_to='chat_attachments/', blank=True, null=True)
    attachment_name = models.CharField(max_length=255, blank=True)
    
    # Message status
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Chat message from {self.sender.get_full_name()} in {self.room.name}"


class GroupJoinRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='join_requests')
    requested_by = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='sent_join_requests')
    target_user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='received_join_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['room', 'target_user']
        ordering = ['-created_at']

    def __str__(self):
        return f"Request to add {self.target_user} to {self.room.name} by {self.requested_by} ({self.status})"

# --- Advanced Multi-Role Chat System Models ---

class AdvancedChatRoom(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_advanced_chatrooms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name or f"ChatRoom {self.id}"

class AdvancedChatRoomParticipant(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('superadmin', 'SuperAdmin'),
    ]
    chatroom = models.ForeignKey(AdvancedChatRoom, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='advanced_chatroom_participations')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_visible = models.BooleanField(default=True)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='added_advanced_chatroom_participants')

    def __str__(self):
        return f"{self.user} in {self.chatroom} as {self.role}"

class AdvancedChatMessage(models.Model):
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('file', 'File'),
        ('system', 'System'),
    ]
    chatroom = models.ForeignKey(AdvancedChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='advanced_chat_messages')
    message_content = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text')
    sent_at = models.DateTimeField(auto_now_add=True)
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Message {self.id} in {self.chatroom} by {self.sender}"
