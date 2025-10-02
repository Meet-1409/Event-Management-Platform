from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
import uuid


class VendorCategory(models.Model):
    """
    Categories for vendors (Catering, Music, Photography, etc.)
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, default='#28a745')  # Hex color code
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'vendor_categories'
        verbose_name_plural = 'Vendor Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Vendor(models.Model):
    """
    Vendor model for service providers
    """
    VENDOR_STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('verified', 'Verified'),
    ]
    
    # Basic information
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    vendor_id = models.CharField(max_length=20, unique=True, blank=True)
    
    # Category and type
    category = models.ForeignKey(VendorCategory, on_delete=models.CASCADE, related_name='vendors')
    
    # Business information
    business_name = models.CharField(max_length=200, blank=True)
    business_license = models.CharField(max_length=100, blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    years_in_business = models.PositiveIntegerField(default=0)
    
    # Contact information
    contact_person = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField()
    website = models.URLField(blank=True)
    
    # Location
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = CountryField()
    postal_code = models.CharField(max_length=20, blank=True)
    service_areas = models.JSONField(default=list, blank=True)
    travel_radius = models.PositiveIntegerField(default=50)  # in miles/km
    
    # Services and pricing
    description = models.TextField()
    services = models.JSONField(default=list, blank=True)
    pricing_info = models.JSONField(default=dict, blank=True)
    minimum_order = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Availability and capacity
    availability_schedule = models.JSONField(default=dict, blank=True)
    max_events_per_day = models.PositiveIntegerField(default=1)
    is_available = models.BooleanField(default=True)
    
    # Status and verification
    status = models.CharField(max_length=20, choices=VENDOR_STATUS_CHOICES, default='pending')
    is_verified = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        'users.CustomUser', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='verified_vendors'
    )
    verification_date = models.DateTimeField(null=True, blank=True)
    
    # Performance metrics
    total_events_served = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.PositiveIntegerField(default=0)
    success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Profile information
    bio = models.TextField(blank=True)
    profile_image = ProcessedImageField(
        upload_to='vendor_profiles/',
        processors=[ResizeToFill(300, 300)],
        format='JPEG',
        options={'quality': 90},
        blank=True,
        null=True
    )
    
    # SEO and marketing
    featured_until = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'vendors'
        ordering = ['-is_featured', '-average_rating', '-created_at']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.vendor_id:
            self.vendor_id = f"VENDOR{uuid.uuid4().hex[:8].upper()}"
        if not self.slug:
            self.slug = f"{self.name.lower().replace(' ', '-')}-{self.vendor_id.lower()}"
        super().save(*args, **kwargs)
    
    @property
    def is_premium(self):
        return self.average_rating >= 4.5 and self.total_events_served >= 20
    
    @property
    def is_available_for_booking(self):
        return self.is_available and self.status in ['active', 'verified']


class VendorImage(models.Model):
    """
    Images for vendors (portfolio, work samples, etc.)
    """
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='images')
    image = ProcessedImageField(
        upload_to='vendor_images/',
        processors=[ResizeToFill(800, 600)],
        format='JPEG',
        options={'quality': 90}
    )
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'vendor_images'
        ordering = ['order', '-is_primary', '-created_at']
    
    def __str__(self):
        return f"{self.vendor.name} - {self.caption or 'Image'}"
    
    def save(self, *args, **kwargs):
        if self.is_primary:
            # Set all other images of this vendor to not primary
            VendorImage.objects.filter(vendor=self.vendor, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)


class VendorService(models.Model):
    """
    Services offered by vendors
    """
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='vendor_services')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_type = models.CharField(max_length=20, choices=[
        ('fixed', 'Fixed Price'),
        ('per_person', 'Per Person'),
        ('per_hour', 'Per Hour'),
        ('custom', 'Custom Quote'),
    ], default='fixed')
    is_available = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'vendor_services'
        unique_together = ['vendor', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.vendor.name}"


class VendorReview(models.Model):
    """
    Reviews and ratings for vendors
    """
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='vendor_reviews')
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='vendor_reviews', null=True, blank=True)
    
    # Rating and review
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200, blank=True)
    review_text = models.TextField()
    
    # Review categories
    quality_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    service_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    value_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    professionalism_rating = models.PositiveIntegerField(
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
        db_table = 'vendor_reviews'
        ordering = ['-created_at']
        unique_together = ['vendor', 'user', 'event']
    
    def __str__(self):
        return f"Review by {self.user.get_full_name()} for {self.vendor.name}"


class VendorAvailability(models.Model):
    """
    Vendor availability calendar
    """
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='availability')
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
        db_table = 'vendor_availability'
        unique_together = ['vendor', 'date', 'start_time']
        ordering = ['date', 'start_time']
    
    def __str__(self):
        return f"{self.vendor.name} - {self.date} {self.start_time}"


class VendorPackage(models.Model):
    """
    Pre-defined packages for vendors
    """
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='packages')
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
        db_table = 'vendor_packages'
        ordering = ['price']
    
    def __str__(self):
        return f"{self.name} - {self.vendor.name}"


class VendorDocument(models.Model):
    """
    Documents for vendors (licenses, certifications, etc.)
    """
    DOCUMENT_TYPE_CHOICES = [
        ('license', 'Business License'),
        ('insurance', 'Insurance Certificate'),
        ('certification', 'Professional Certification'),
        ('portfolio', 'Portfolio'),
        ('reference', 'Reference Letter'),
        ('other', 'Other'),
    ]
    
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    file = models.FileField(upload_to='vendor_documents/')
    
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
        related_name='verified_vendor_documents'
    )
    verification_date = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'vendor_documents'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.vendor.name}"


class VendorSpecialization(models.Model):
    """
    Specializations for vendors
    """
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='specializations')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    years_experience = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'vendor_specializations'
        unique_together = ['vendor', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.vendor.name}"
