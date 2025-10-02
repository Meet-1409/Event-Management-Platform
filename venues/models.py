from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
import uuid


class VenueCategory(models.Model):
    """
    Categories for venues (Wedding, Corporate, Birthday, etc.)
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, default='#007bff')  # Hex color code
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'venue_categories'
        verbose_name_plural = 'Venue Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Venue(models.Model):
    """
    Venue model for comprehensive event management
    """
    VENUE_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
        ('booked', 'Fully Booked'),
        ('featured', 'Featured'),
    ]
    
    # Basic information
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    venue_id = models.CharField(max_length=20, unique=True, blank=True)
    
    # Category and type
    category = models.ForeignKey(VenueCategory, on_delete=models.CASCADE, related_name='venues')
    
    # Location information
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = CountryField()
    postal_code = models.CharField(max_length=20, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Capacity and dimensions
    capacity_min = models.PositiveIntegerField(default=1)
    capacity_max = models.PositiveIntegerField()
    area_sqft = models.PositiveIntegerField(null=True, blank=True)
    ceiling_height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_person = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    deposit_required = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cancellation_policy = models.TextField(blank=True)
    
    # Features and amenities
    description = models.TextField()
    features = models.JSONField(default=list, blank=True)
    restrictions = models.JSONField(default=list, blank=True)
    
    # Contact information
    contact_person = models.CharField(max_length=100, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    
    # Status and visibility
    status = models.CharField(max_length=20, choices=VENUE_STATUS_CHOICES, default='active')
    is_featured = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    featured_until = models.DateTimeField(null=True, blank=True)
    
    # Performance metrics
    total_bookings = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'venues'
        ordering = ['-is_featured', '-average_rating', '-created_at']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.venue_id:
            self.venue_id = f"VENUE{uuid.uuid4().hex[:8].upper()}"
        if not self.slug:
            self.slug = f"{self.name.lower().replace(' ', '-')}-{self.venue_id.lower()}"
        super().save(*args, **kwargs)
    
    @property
    def is_available(self):
        return self.status in ['active', 'featured']
    
    @property
    def main_image(self):
        return self.images.filter(is_primary=True).first()


class VenueImage(models.Model):
    """
    Images for venues
    """
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='images')
    image = ProcessedImageField(
        upload_to='venue_images/',
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
        db_table = 'venue_images'
        ordering = ['order', '-is_primary', '-created_at']
    
    def __str__(self):
        return f"{self.venue.name} - {self.caption or 'Image'}"
    
    def save(self, *args, **kwargs):
        if self.is_primary:
            # Set all other images of this venue to not primary
            VenueImage.objects.filter(venue=self.venue, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)





class VenueReview(models.Model):
    """
    Reviews and ratings for venues
    """
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='venue_reviews')
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='venue_reviews', null=True, blank=True)
    
    # Rating and review
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200, blank=True)
    review_text = models.TextField()
    
    # Review categories
    cleanliness_rating = models.PositiveIntegerField(
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
    location_rating = models.PositiveIntegerField(
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
        db_table = 'venue_reviews'
        ordering = ['-created_at']
        unique_together = ['venue', 'user', 'event']
    
    def __str__(self):
        return f"Review by {self.user.get_full_name()} for {self.venue.name}"


class VenueAvailability(models.Model):
    """
    Venue availability calendar
    """
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='availability')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # Availability status
    is_available = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)
    block_reason = models.CharField(max_length=200, blank=True)
    
    # Pricing for specific dates
    special_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'venue_availability'
        unique_together = ['venue', 'date', 'start_time']
        ordering = ['date', 'start_time']
    
    def __str__(self):
        return f"{self.venue.name} - {self.date} {self.start_time}"


class VenuePackage(models.Model):
    """
    Pre-defined packages for venues
    """
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='packages')
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
        db_table = 'venue_packages'
        ordering = ['price']
    
    def __str__(self):
        return f"{self.name} - {self.venue.name}"


class VenueFacility(models.Model):
    """
    Facilities and amenities available at venues
    """
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='facilities')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    is_available = models.BooleanField(default=True)
    additional_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'venue_facilities'
        verbose_name_plural = 'Venue Facilities'
        unique_together = ['venue', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.venue.name}"
