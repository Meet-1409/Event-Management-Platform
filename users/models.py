from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
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
    country = CountryField(blank=True, default='IN')
    
    # Additional profile information
    bio = models.TextField(max_length=500, blank=True, help_text='Tell us about yourself')
    website = models.URLField(blank=True, help_text='Your website or portfolio')
    linkedin_profile = models.URLField(blank=True, help_text='Your LinkedIn profile')
    twitter_handle = models.CharField(max_length=50, blank=True, help_text='Your Twitter handle (without @)')
    
    # Professional information
    company = models.CharField(max_length=100, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    experience_years = models.PositiveIntegerField(null=True, blank=True, help_text='Years of professional experience')
    
    # Event management specific fields
    specializations = models.JSONField(default=list, blank=True, help_text='Areas of expertise')
    languages = models.JSONField(default=list, blank=True, help_text='Languages you speak')
    
    # Account status
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Settings
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    newsletter_subscription = models.BooleanField(default=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        return self.first_name
    
    @property
    def is_manager(self):
        return self.user_type == 'manager'
    
    @property
    def is_admin(self):
        return self.user_type == 'admin'
    
    @property
    def is_regular_user(self):
        return self.user_type == 'user'
    
    def get_profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return '/static/images/default-avatar.png'


class UserRoleRequest(models.Model):
    """
    Model to handle user role upgrade requests that need admin approval
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='role_requests')
    requested_role = models.CharField(
        max_length=10, 
        choices=CustomUser.USER_TYPE_CHOICES,
        help_text='Role the user is requesting'
    )
    current_role = models.CharField(
        max_length=10,
        choices=CustomUser.USER_TYPE_CHOICES,
        help_text='User\'s current role'
    )
    reason = models.TextField(
        help_text='Why the user wants this role upgrade',
        blank=True
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    reviewed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_requests',
        help_text='Admin who reviewed this request'
    )
    review_notes = models.TextField(
        blank=True,
        help_text='Admin notes about the decision'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'requested_role', 'status']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_requested_role_display()} Request"
    
    def approve(self, admin_user, notes=''):
        """Approve the role request"""
        self.status = 'approved'
        self.reviewed_by = admin_user
        self.review_notes = notes
        self.reviewed_at = timezone.now()
        
        # Update user's role
        self.user.user_type = self.requested_role
        self.user.save()
        
        self.save()
    
    def reject(self, admin_user, notes=''):
        """Reject the role request"""
        self.status = 'rejected'
        self.reviewed_by = admin_user
        self.review_notes = notes
        self.reviewed_at = timezone.now()
        self.save()