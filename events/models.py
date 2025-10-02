from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
import uuid


class EventType(models.Model):
    """
    Types of events (e.g., Wedding, Corporate, Birthday, etc.)
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, default='#007bff')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'event_types'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Event(models.Model):
    """
    Main event model for booking and management
    """
    EVENT_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('postponed', 'Postponed'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partial Payment'),
        ('paid', 'Fully Paid'),
        ('refunded', 'Refunded'),
        ('failed', 'Payment Failed'),
    ]
    
    # Basic information
    event_id = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.ForeignKey(EventType, on_delete=models.CASCADE, related_name='events')
    
    # Event details
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    expected_guests = models.PositiveIntegerField()
    actual_guests = models.PositiveIntegerField(null=True, blank=True)
    
    # Venue and location
    venue = models.ForeignKey('venues.Venue', on_delete=models.CASCADE, related_name='events')
    venue_package = models.ForeignKey('venues.VenuePackage', on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    
    # Event organizer
    organizer = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='organized_events')
    event_manager = models.ForeignKey('users.CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_events')
    
    # Status and payment
    status = models.CharField(max_length=20, choices=EVENT_STATUS_CHOICES, default='draft')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Budget and pricing
    total_budget = models.DecimalField(max_digits=12, decimal_places=2)
    venue_cost = models.DecimalField(max_digits=10, decimal_places=2)
    vendor_costs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    manager_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Event theme and customization
    theme = models.CharField(max_length=100, blank=True)
    color_scheme = models.JSONField(default=list, blank=True)
    special_requirements = models.TextField(blank=True)
    dietary_restrictions = models.JSONField(default=list, blank=True)
    
    # Event setup and logistics
    setup_time = models.TimeField(null=True, blank=True)
    cleanup_time = models.TimeField(null=True, blank=True)
    setup_requirements = models.JSONField(default=list, blank=True)
    
    # Images and media
    event_image = ProcessedImageField(
        upload_to='event_images/',
        processors=[ResizeToFill(800, 600)],
        format='JPEG',
        options={'quality': 90},
        blank=True,
        null=True
    )
    
    # Advanced categorization
    sub_category = models.CharField(max_length=100, blank=True, help_text='Sub-category (e.g., Football, Java, Baking)')
    skill_level = models.CharField(max_length=30, blank=True, help_text='Skill level (e.g., Beginner, Intermediate, Advanced)')
    format = models.CharField(max_length=30, blank=True, help_text='Format (e.g., In-person, Online, Drive-through)')
    tags = models.JSONField(default=list, blank=True, help_text='Tags for advanced filtering')
    
    # Event visibility
    is_public = models.BooleanField(default=True, help_text='Public events are visible to all users, private events are only visible to organizers')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'events'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.start_date}"
    
    def save(self, *args, **kwargs):
        if not self.event_id:
            self.event_id = f"EVT{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def duration_hours(self):
        """Calculate event duration in hours"""
        from datetime import datetime, timedelta
        start = datetime.combine(self.start_date, self.start_time)
        end = datetime.combine(self.end_date, self.end_time)
        duration = end - start
        return duration.total_seconds() / 3600
    
    @property
    def is_upcoming(self):
        from django.utils import timezone
        return self.start_date > timezone.now().date()
    
    @property
    def is_ongoing(self):
        from django.utils import timezone
        now = timezone.now()
        start = now.replace(year=self.start_date.year, month=self.start_date.month, day=self.start_date.day,
                           hour=self.start_time.hour, minute=self.start_time.minute)
        end = now.replace(year=self.end_date.year, month=self.end_date.month, day=self.end_date.day,
                         hour=self.end_time.hour, minute=self.end_time.minute)
        return start <= now <= end


class EventVendor(models.Model):
    """
    Vendors associated with events
    """
    VENDOR_TYPE_CHOICES = [
        ('catering', 'Catering'),
        ('music', 'Music/DJ'),
        ('photography', 'Photography'),
        ('videography', 'Videography'),
        ('decor', 'Decoration'),
        ('transportation', 'Transportation'),
        ('entertainment', 'Entertainment'),
        ('security', 'Security'),
        ('cleaning', 'Cleaning'),
        ('other', 'Other'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='vendors')
    vendor = models.ForeignKey('vendors.Vendor', on_delete=models.CASCADE, related_name='event_bookings')
    vendor_type = models.CharField(max_length=20, choices=VENDOR_TYPE_CHOICES)
    
    # Service details
    service_description = models.TextField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    quantity = models.PositiveIntegerField(default=1)
    
    # Pricing
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status
    is_confirmed = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    
    # Notes
    special_requirements = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'event_vendors'
        unique_together = ['event', 'vendor', 'vendor_type']
    
    def __str__(self):
        return f"{self.vendor.name} - {self.event.title}"
    
    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class EventGuest(models.Model):
    """
    Guest list for events
    """
    GUEST_STATUS_CHOICES = [
        ('invited', 'Invited'),
        ('confirmed', 'Confirmed'),
        ('declined', 'Declined'),
        ('maybe', 'Maybe'),
        ('attended', 'Attended'),
        ('no_show', 'No Show'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='guests')
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Guest details
    is_primary_guest = models.BooleanField(default=False)
    plus_ones = models.PositiveIntegerField(default=0)
    dietary_restrictions = models.TextField(blank=True)
    special_requirements = models.TextField(blank=True)
    
    # RSVP and attendance
    status = models.CharField(max_length=20, choices=GUEST_STATUS_CHOICES, default='invited')
    rsvp_date = models.DateTimeField(null=True, blank=True)
    attended = models.BooleanField(default=False)
    
    # Seating and table assignment
    table_number = models.PositiveIntegerField(null=True, blank=True)
    seat_number = models.PositiveIntegerField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'event_guests'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.event.title}"


class EventTimeline(models.Model):
    """
    Event timeline and schedule
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='timeline')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Timing
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    
    # Assignment
    responsible_person = models.CharField(max_length=100, blank=True)
    vendor = models.ForeignKey('vendors.Vendor', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Status
    is_completed = models.BooleanField(default=False)
    is_critical = models.BooleanField(default=False)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'event_timeline'
        ordering = ['start_time']
    
    def __str__(self):
        return f"{self.title} - {self.event.title}"


class EventChecklist(models.Model):
    """
    Event planning checklist
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='checklist')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Task details
    due_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], default='medium')
    
    # Assignment
    assigned_to = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=50, blank=True)
    
    # Status
    is_completed = models.BooleanField(default=False)
    completed_date = models.DateTimeField(null=True, blank=True)
    completed_by = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'event_checklist'
        ordering = ['due_date', 'priority']
    
    def __str__(self):
        return f"{self.title} - {self.event.title}"


class EventBudget(models.Model):
    """
    Detailed budget breakdown for events
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='budget_items')
    category = models.CharField(max_length=100)
    item_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Budget details
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    vendor = models.ForeignKey('vendors.Vendor', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Payment status
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'event_budget'
        ordering = ['category', 'item_name']
    
    def __str__(self):
        return f"{self.item_name} - {self.event.title}"
    
    @property
    def variance(self):
        if self.actual_cost:
            return self.actual_cost - self.estimated_cost
        return 0


class EventDocument(models.Model):
    """
    Documents associated with events
    """
    DOCUMENT_TYPE_CHOICES = [
        ('contract', 'Contract'),
        ('invoice', 'Invoice'),
        ('receipt', 'Receipt'),
        ('permit', 'Permit'),
        ('insurance', 'Insurance'),
        ('floor_plan', 'Floor Plan'),
        ('menu', 'Menu'),
        ('timeline', 'Timeline'),
        ('guest_list', 'Guest List'),
        ('other', 'Other'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    file = models.FileField(upload_to='event_documents/')
    
    # Document details
    description = models.TextField(blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    file_type = models.CharField(max_length=50, blank=True)
    
    # Access control
    is_public = models.BooleanField(default=False)
    shared_with = models.JSONField(default=list, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'event_documents'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.event.title}"


class EventNote(models.Model):
    """
    Notes and comments for events
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='event_notes')
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    
    # Note type
    note_type = models.CharField(max_length=20, choices=[
        ('general', 'General'),
        ('logistics', 'Logistics'),
        ('vendor', 'Vendor'),
        ('guest', 'Guest'),
        ('financial', 'Financial'),
        ('emergency', 'Emergency'),
    ], default='general')
    
    # Visibility
    is_private = models.BooleanField(default=False)
    is_important = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'event_notes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Note by {self.author.get_full_name()} - {self.event.title}"


class Registration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    guest_count = models.IntegerField(default=1, help_text="Number of guests")
    special_requirements = models.TextField(blank=True, null=True, help_text="Any special requirements or notes")
    source = models.CharField(max_length=50, blank=True, null=True, help_text="How they heard about the event")
    terms_accepted = models.BooleanField(default=False, help_text="Terms and conditions accepted")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.event.title}"


class EventReview(models.Model):
    """User reviews and ratings for events"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='event_reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], help_text="Rating from 1 to 5 stars")
    title = models.CharField(max_length=200)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['event', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.event.title} - {self.rating} stars"
    
    @property
    def stars_display(self):
        """Return HTML for star display"""
        full_stars = self.rating
        empty_stars = 5 - self.rating
        return '★' * full_stars + '☆' * empty_stars
