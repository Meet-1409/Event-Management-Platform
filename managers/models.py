from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
import uuid


class ManagerSpecialization(models.Model):
    """
    Specializations for event managers
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, blank=True)
    icon = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'manager_specializations'
        ordering = ['category', 'name']
    
    def __str__(self):
        return self.name


class EventManager(models.Model):
    """
    Professional event manager profiles
    """
    MANAGER_STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('verified', 'Verified'),
    ]
    
    # Basic information
    user = models.OneToOneField('users.CustomUser', on_delete=models.CASCADE, related_name='event_manager_profile')
    manager_id = models.CharField(max_length=20, unique=True, blank=True)
    
    # Professional information
    company_name = models.CharField(max_length=200, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    
    # Specializations
    specializations = models.ManyToManyField(ManagerSpecialization, related_name='managers', blank=True)
    certifications = models.JSONField(default=list, blank=True)
    awards = models.JSONField(default=list, blank=True)
    
    # Professional documents
    resume = models.FileField(upload_to='manager_resumes/', blank=True)
    portfolio = models.FileField(upload_to='manager_portfolios/', blank=True)
    references = models.JSONField(default=list, blank=True)
    
    # Business information
    business_license = models.CharField(max_length=100, blank=True)
    insurance_info = models.JSONField(default=dict, blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    
    # Service areas
    service_areas = models.JSONField(default=list, blank=True)
    travel_radius = models.PositiveIntegerField(default=50)  # in miles/km
    
    # Pricing
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    package_pricing = models.JSONField(default=dict, blank=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Availability
    availability_schedule = models.JSONField(default=dict, blank=True)
    max_events_per_month = models.PositiveIntegerField(default=10)
    is_available = models.BooleanField(default=True)
    
    # Performance metrics
    total_events_managed = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.PositiveIntegerField(default=0)
    success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Verification status
    status = models.CharField(max_length=20, choices=MANAGER_STATUS_CHOICES, default='pending')
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        'users.CustomUser', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='verified_event_managers'
    )
    
    # Profile information
    bio = models.TextField(blank=True)
    profile_image = ProcessedImageField(
        upload_to='manager_profiles/',
        processors=[ResizeToFill(300, 300)],
        format='JPEG',
        options={'quality': 90},
        blank=True,
        null=True
    )
    
    # Contact preferences
    preferred_contact_method = models.CharField(max_length=20, choices=[
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
    ], default='email')
    
    # SEO and marketing
    featured = models.BooleanField(default=False)
    featured_until = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'event_managers'
        ordering = ['-featured', '-average_rating', '-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - Event Manager"
    
    def save(self, *args, **kwargs):
        if not self.manager_id:
            self.manager_id = f"EM{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def is_premium(self):
        return self.average_rating >= 4.5 and self.total_events_managed >= 20
    
    @property
    def is_available_for_booking(self):
        return self.is_available and self.status in ['active', 'verified']


class ManagerReview(models.Model):
    """
    Reviews and ratings for event managers
    """
    manager = models.ForeignKey(EventManager, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='manager_reviews')
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='manager_reviews', null=True, blank=True)
    
    # Rating and review
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200, blank=True)
    review_text = models.TextField()
    
    # Review categories
    professionalism_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    communication_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    expertise_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    value_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    
    # Review status
    is_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    is_helpful = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'manager_reviews'
        ordering = ['-created_at']
        unique_together = ['manager', 'user', 'event']
    
    def __str__(self):
        return f"Review by {self.user.get_full_name()} for {self.manager.user.get_full_name()}"


class ManagerAvailability(models.Model):
    """
    Event manager availability calendar
    """
    manager = models.ForeignKey(EventManager, on_delete=models.CASCADE, related_name='availability')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # Availability status
    is_available = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)
    block_reason = models.CharField(max_length=200, blank=True)
    
    # Pricing for specific dates
    special_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'manager_availability'
        unique_together = ['manager', 'date', 'start_time']
        ordering = ['date', 'start_time']
    
    def __str__(self):
        return f"{self.manager.user.get_full_name()} - {self.date} {self.start_time}"


class ManagerPackage(models.Model):
    """
    Pre-defined packages for event managers
    """
    manager = models.ForeignKey(EventManager, on_delete=models.CASCADE, related_name='packages')
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    # Package details
    duration_hours = models.PositiveIntegerField(default=4)
    max_guests = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Package inclusions
    inclusions = models.JSONField(default=list, blank=True)
    exclusions = models.JSONField(default=list, blank=True)
    
    # Package availability
    is_active = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'manager_packages'
        ordering = ['price']
    
    def __str__(self):
        return f"{self.name} - {self.manager.user.get_full_name()}"


class ManagerDocument(models.Model):
    """
    Documents for event managers (licenses, certifications, etc.)
    """
    DOCUMENT_TYPE_CHOICES = [
        ('license', 'Business License'),
        ('insurance', 'Insurance Certificate'),
        ('certification', 'Professional Certification'),
        ('portfolio', 'Portfolio'),
        ('resume', 'Resume'),
        ('reference', 'Reference Letter'),
        ('other', 'Other'),
    ]
    
    manager = models.ForeignKey(EventManager, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    file = models.FileField(upload_to='manager_documents/')
    
    # Document details
    description = models.TextField(blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    file_type = models.CharField(max_length=50, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    
    # Verification status
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        'users.CustomUser', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='verified_manager_documents'
    )
    verification_date = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'manager_documents'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.manager.user.get_full_name()}"


class ManagerAssignment(models.Model):
    """
    Assignments of event managers to users/events
    """
    ASSIGNMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Basic information
    assignment_id = models.CharField(max_length=50, unique=True, blank=True)
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='manager_assignments')
    manager = models.ForeignKey(EventManager, on_delete=models.CASCADE, related_name='assignments')
    
    # Assignment details
    status = models.CharField(max_length=20, choices=ASSIGNMENT_STATUS_CHOICES, default='pending')
    assigned_by = models.ForeignKey(
        'users.CustomUser', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_managers'
    )
    
    # Event context
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='manager_assignments', null=True, blank=True)
    event_type = models.CharField(max_length=100, blank=True)
    expected_guests = models.PositiveIntegerField(null=True, blank=True)
    budget_range = models.CharField(max_length=50, blank=True)
    
    # Assignment details
    assignment_reason = models.TextField(blank=True)
    special_requirements = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'manager_assignments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Assignment {self.assignment_id} - {self.user.get_full_name()} to {self.manager.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.assignment_id:
            self.assignment_id = f"ASSIGN{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class ManagerNote(models.Model):
    """
    Notes and comments for event managers
    """
    manager = models.ForeignKey(EventManager, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='manager_notes')
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    
    # Note type
    note_type = models.CharField(max_length=20, choices=[
        ('general', 'General'),
        ('performance', 'Performance'),
        ('feedback', 'Feedback'),
        ('recommendation', 'Recommendation'),
        ('warning', 'Warning'),
        ('praise', 'Praise'),
    ], default='general')
    
    # Visibility
    is_private = models.BooleanField(default=False)
    is_important = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'manager_notes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Note by {self.author.get_full_name()} - {self.manager.user.get_full_name()}"
