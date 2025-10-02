from django.contrib import admin
from .models import (
    VendorCategory, Vendor, VendorImage, VendorService, VendorReview,
    VendorAvailability, VendorPackage, VendorDocument, VendorSpecialization
)

@admin.register(VendorCategory)
class VendorCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'color')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('name',)
    fieldsets = (
        ('Category Info', {
            'fields': ('name', 'is_active'),
            'description': 'Basic category information.'
        }),
        ('Details', {
            'fields': ('description', 'icon', 'color'),
            'description': 'Category description and styling.'
        }),
    )

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'contact_email', 'status', 'average_rating', 'total_events_served', 'is_verified')
    search_fields = ('name', 'category__name', 'contact_email', 'business_name')
    list_filter = ('category', 'status', 'is_verified', 'is_featured', 'is_available')
    ordering = ('-average_rating', '-created_at')
    readonly_fields = ('vendor_id', 'slug', 'total_events_served', 'average_rating', 'total_reviews', 'success_rate')
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'vendor_id', 'slug', 'category', 'status'),
            'description': 'Main vendor information.'
        }),
        ('Business Info', {
            'fields': ('business_name', 'business_license', 'tax_id', 'years_in_business'),
            'description': 'Business registration and experience.'
        }),
        ('Contact', {
            'fields': ('contact_person', 'contact_phone', 'contact_email', 'website'),
            'description': 'Contact information.'
        }),
        ('Location', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code', 'service_areas', 'travel_radius'),
            'description': 'Vendor location and service areas.'
        }),
        ('Services', {
            'fields': ('description', 'services', 'pricing_info', 'minimum_order'),
            'description': 'Services offered and pricing.'
        }),
        ('Availability', {
            'fields': ('availability_schedule', 'max_events_per_day', 'is_available'),
            'description': 'Vendor availability and capacity.'
        }),
        ('Performance', {
            'fields': ('total_events_served', 'average_rating', 'total_reviews', 'success_rate'),
            'description': 'Performance metrics (read-only).'
        }),
        ('Verification', {
            'fields': ('is_verified', 'verified_by', 'verification_date'),
            'description': 'Verification status and details.'
        }),
        ('Profile', {
            'fields': ('bio', 'profile_image', 'is_featured', 'featured_until'),
            'description': 'Profile information and featured status.'
        }),
    )

@admin.register(VendorImage)
class VendorImageAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'caption', 'is_primary', 'order', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('vendor__name', 'caption')
    ordering = ('vendor', 'order', '-is_primary')
    fieldsets = (
        ('Image Info', {
            'fields': ('vendor', 'image', 'caption'),
            'description': 'Basic image information.'
        }),
        ('Display', {
            'fields': ('is_primary', 'order'),
            'description': 'Image display settings.'
        }),
    )

@admin.register(VendorService)
class VendorServiceAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'name', 'price', 'price_type', 'is_available')
    list_filter = ('price_type', 'is_available', 'created_at')
    search_fields = ('vendor__name', 'name', 'description')
    ordering = ('vendor', 'name')
    fieldsets = (
        ('Service Info', {
            'fields': ('vendor', 'name', 'description'),
            'description': 'Basic service information.'
        }),
        ('Pricing', {
            'fields': ('price', 'price_type'),
            'description': 'Service pricing details.'
        }),
        ('Status', {
            'fields': ('is_available',),
            'description': 'Service availability.'
        }),
    )

@admin.register(VendorReview)
class VendorReviewAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'user', 'rating', 'is_verified', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_verified', 'is_approved', 'created_at')
    search_fields = ('vendor__name', 'user__username', 'title', 'review_text')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Review Info', {
            'fields': ('vendor', 'user', 'event', 'rating'),
            'description': 'Basic review information.'
        }),
        ('Review Content', {
            'fields': ('title', 'review_text'),
            'description': 'Review title and detailed text.'
        }),
        ('Detailed Ratings', {
            'fields': ('quality_rating', 'service_rating', 'value_rating', 'professionalism_rating'),
            'description': 'Detailed rating breakdown.'
        }),
        ('Status', {
            'fields': ('is_verified', 'is_approved', 'is_helpful'),
            'description': 'Review status and helpfulness.'
        }),
    )

@admin.register(VendorAvailability)
class VendorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'date', 'start_time', 'end_time', 'is_available', 'is_blocked')
    list_filter = ('is_available', 'is_blocked', 'date')
    search_fields = ('vendor__name', 'block_reason')
    ordering = ('date', 'start_time')
    fieldsets = (
        ('Availability Info', {
            'fields': ('vendor', 'date', 'start_time', 'end_time'),
            'description': 'Vendor availability schedule.'
        }),
        ('Status', {
            'fields': ('is_available', 'is_blocked', 'block_reason'),
            'description': 'Availability status and blocking.'
        }),
        ('Pricing', {
            'fields': ('special_rate',),
            'description': 'Special pricing for this time slot.'
        }),
    )

@admin.register(VendorPackage)
class VendorPackageAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'name', 'duration_hours', 'max_guests', 'price', 'is_active', 'is_popular')
    list_filter = ('is_active', 'is_popular', 'duration_hours')
    search_fields = ('vendor__name', 'name', 'description')
    ordering = ('price',)
    fieldsets = (
        ('Package Info', {
            'fields': ('vendor', 'name', 'description'),
            'description': 'Basic package information.'
        }),
        ('Package Details', {
            'fields': ('duration_hours', 'max_guests', 'price'),
            'description': 'Package specifications and pricing.'
        }),
        ('Inclusions', {
            'fields': ('inclusions', 'exclusions'),
            'description': 'What is included and excluded in the package.'
        }),
        ('Status', {
            'fields': ('is_active', 'is_popular'),
            'description': 'Package availability and popularity.'
        }),
    )

@admin.register(VendorDocument)
class VendorDocumentAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'title', 'document_type', 'is_verified', 'expiry_date', 'created_at')
    list_filter = ('document_type', 'is_verified', 'created_at')
    search_fields = ('vendor__name', 'title', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('file_size', 'file_type', 'created_at', 'updated_at')
    fieldsets = (
        ('Document Info', {
            'fields': ('vendor', 'title', 'document_type'),
            'description': 'Basic document information.'
        }),
        ('File', {
            'fields': ('file', 'file_size', 'file_type'),
            'description': 'Document file and metadata.'
        }),
        ('Details', {
            'fields': ('description', 'expiry_date'),
            'description': 'Document description and expiry date.'
        }),
        ('Verification', {
            'fields': ('is_verified', 'verified_by', 'verification_date'),
            'description': 'Document verification status.'
        }),
    )

@admin.register(VendorSpecialization)
class VendorSpecializationAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'name', 'years_experience', 'created_at')
    search_fields = ('vendor__name', 'name', 'description')
    ordering = ('vendor', 'name')
    fieldsets = (
        ('Specialization Info', {
            'fields': ('vendor', 'name', 'description'),
            'description': 'Basic specialization information.'
        }),
        ('Experience', {
            'fields': ('years_experience',),
            'description': 'Years of experience in this specialization.'
        }),
    )
