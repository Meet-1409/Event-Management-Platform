from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django_countries.fields import CountryField
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill


class CustomUser(AbstractUser):
    """
    Custom User Model with role-based authentication
    """
    USER_TYPE_CHOICES = [
        ('user', 'Regular User'),
        ('manager', 'Event Manager'),
        ('admin', 'Administrator'),
    ]
    
    # Basic fields
    email = models.EmailField(_('email address'), unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='user')
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    
    # Profile fields
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], blank=True)
    profile_picture = ProcessedImageField(
        upload_to='profile_pictures/',
        processors=[ResizeToFill(200, 200)],
        format='JPEG',
        options={'quality': 90},
        blank=True,
        null=True
    )
    
    # Address fields
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = CountryField(blank=True)
    
    # Account status
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    # Preferences
    notification_email = models.BooleanField(default=True)
    notification_sms = models.BooleanField(default=False)
    notification_push = models.BooleanField(default=True)
    
    # Social media links
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    
    # Emergency contact
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = 'users'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        return self.first_name
    
    @property
    def is_event_manager(self):
        return self.user_type == 'manager'
    
    @property
    def is_regular_user(self):
        return self.user_type == 'user'
    
    @property
    def is_administrator(self):
        return self.user_type == 'admin'
    
    def get_profile_completion_percentage(self):
        """Calculate profile completion percentage"""
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'date_of_birth', 'gender', 'address_line1', 'city',
            'state', 'postal_code', 'country'
        ]
        completed = sum(1 for field in fields if getattr(self, field))
        return int((completed / len(fields)) * 100)


class UserProfile(models.Model):
    """
    Extended profile information for regular users
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='user_profile')
    
    # Event preferences
    preferred_event_types = models.JSONField(default=list, blank=True)
    preferred_venues = models.JSONField(default=list, blank=True)
    budget_range = models.CharField(max_length=50, blank=True)
    
    # Event history
    total_events_organized = models.PositiveIntegerField(default=0)
    total_events_attended = models.PositiveIntegerField(default=0)
    
    # Preferences
    dietary_restrictions = models.JSONField(default=list, blank=True)
    accessibility_requirements = models.JSONField(default=list, blank=True)
    
    # Social preferences
    preferred_languages = models.JSONField(default=list, blank=True)
    cultural_preferences = models.JSONField(default=list, blank=True)
    
    # Communication preferences
    preferred_contact_method = models.CharField(max_length=20, choices=[
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
    ], default='email')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"Profile for {self.user.get_full_name()}"


class EventManagerProfile(models.Model):
    """
    Extended profile information for event managers
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='manager_profile')
    
    # Professional information
    company_name = models.CharField(max_length=200, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    
    # Specializations
    specializations = models.JSONField(default=list, blank=True)
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
    
    # Availability
    availability_schedule = models.JSONField(default=dict, blank=True)
    max_events_per_month = models.PositiveIntegerField(default=10)
    
    # Performance metrics
    total_events_managed = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.PositiveIntegerField(default=0)
    
    # Verification status
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='verified_managers'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'event_manager_profiles'
    
    def __str__(self):
        return f"Manager Profile for {self.user.get_full_name()}"
    
    def get_verification_status_display(self):
        if self.is_verified:
            return "Verified"
        return "Pending Verification"


class UserSession(models.Model):
    """
    Track user sessions for analytics and security
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_sessions'
    
    def __str__(self):
        return f"Session for {self.user.email}"


class UserActivity(models.Model):
    """
    Track user activities for analytics
    """
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('profile_update', 'Profile Update'),
        ('venue_view', 'Venue View'),
        ('event_booking', 'Event Booking'),
        ('payment', 'Payment'),
        ('message_sent', 'Message Sent'),
        ('consultation_request', 'Consultation Request'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_activities'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.get_activity_type_display()} at {self.created_at}"
