from django.contrib import admin
from .models import (
    ManagerSpecialization, EventManager, ManagerReview, ManagerAvailability,
    ManagerPackage, ManagerDocument, ManagerAssignment, ManagerNote
)

@admin.register(ManagerSpecialization)
class ManagerSpecializationAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('category', 'name')
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'category', 'is_active'),
            'description': 'Main details about the specialization.'
        }),
        ('Details', {
            'fields': ('description', 'icon'),
            'description': 'Description and icon for the specialization.'
        }),
    )

@admin.register(EventManager)
class EventManagerAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'status', 'average_rating', 'total_events_managed', 'is_verified')
    list_filter = ('status', 'is_verified', 'is_available', 'featured')
    search_fields = ('user__username', 'user__email', 'company_name', 'job_title')
    ordering = ('-average_rating', '-created_at')
    readonly_fields = ('manager_id', 'total_events_managed', 'average_rating', 'total_reviews', 'success_rate')
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'manager_id', 'status', 'is_verified'),
            'description': 'Main manager information and verification status.'
        }),
        ('Professional Info', {
            'fields': ('company_name', 'job_title', 'years_of_experience', 'bio'),
            'description': 'Professional background and experience.'
        }),
        ('Specializations', {
            'fields': ('specializations', 'certifications', 'awards'),
            'description': 'Manager skills and achievements.'
        }),
        ('Business Info', {
            'fields': ('business_license', 'insurance_info', 'tax_id'),
            'description': 'Business registration and legal information.'
        }),
        ('Service Areas', {
            'fields': ('service_areas', 'travel_radius'),
            'description': 'Where the manager provides services.'
        }),
        ('Pricing', {
            'fields': ('hourly_rate', 'package_pricing', 'consultation_fee'),
            'description': 'Manager pricing structure.'
        }),
        ('Availability', {
            'fields': ('availability_schedule', 'max_events_per_month', 'is_available'),
            'description': 'Manager availability and capacity.'
        }),
        ('Performance', {
            'fields': ('total_events_managed', 'average_rating', 'total_reviews', 'success_rate'),
            'description': 'Performance metrics (read-only).'
        }),
        ('Verification', {
            'fields': ('verification_date', 'verified_by'),
            'description': 'Verification details.'
        }),
        ('Profile', {
            'fields': ('profile_image', 'preferred_contact_method'),
            'description': 'Profile image and contact preferences.'
        }),
        ('Marketing', {
            'fields': ('featured', 'featured_until'),
            'description': 'Featured status for marketing.'
        }),
    )

@admin.register(ManagerReview)
class ManagerReviewAdmin(admin.ModelAdmin):
    list_display = ('manager', 'user', 'rating', 'is_verified', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_verified', 'is_approved', 'created_at')
    search_fields = ('manager__user__username', 'user__username', 'title', 'review_text')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Review Info', {
            'fields': ('manager', 'user', 'event', 'rating'),
            'description': 'Basic review information.'
        }),
        ('Review Content', {
            'fields': ('title', 'review_text'),
            'description': 'Review title and detailed text.'
        }),
        ('Detailed Ratings', {
            'fields': ('professionalism_rating', 'communication_rating', 'expertise_rating', 'value_rating'),
            'description': 'Detailed rating breakdown.'
        }),
        ('Status', {
            'fields': ('is_verified', 'is_approved', 'is_helpful'),
            'description': 'Review status and helpfulness.'
        }),
    )

@admin.register(ManagerAvailability)
class ManagerAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('manager', 'date', 'start_time', 'end_time', 'is_available', 'is_blocked')
    list_filter = ('is_available', 'is_blocked', 'date')
    search_fields = ('manager__user__username', 'block_reason')
    ordering = ('date', 'start_time')
    fieldsets = (
        ('Availability Info', {
            'fields': ('manager', 'date', 'start_time', 'end_time'),
            'description': 'Manager availability schedule.'
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

@admin.register(ManagerPackage)
class ManagerPackageAdmin(admin.ModelAdmin):
    list_display = ('manager', 'name', 'duration_hours', 'max_guests', 'price', 'is_active', 'is_popular')
    list_filter = ('is_active', 'is_popular', 'duration_hours')
    search_fields = ('manager__user__username', 'name', 'description')
    ordering = ('price',)
    fieldsets = (
        ('Package Info', {
            'fields': ('manager', 'name', 'description'),
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

@admin.register(ManagerDocument)
class ManagerDocumentAdmin(admin.ModelAdmin):
    list_display = ('manager', 'title', 'document_type', 'is_verified', 'expiry_date', 'created_at')
    list_filter = ('document_type', 'is_verified', 'created_at')
    search_fields = ('manager__user__username', 'title', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('file_size', 'file_type', 'created_at', 'updated_at')
    fieldsets = (
        ('Document Info', {
            'fields': ('manager', 'title', 'document_type'),
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

@admin.register(ManagerAssignment)
class ManagerAssignmentAdmin(admin.ModelAdmin):
    list_display = ('assignment_id', 'user', 'manager', 'status', 'event', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('assignment_id', 'user__username', 'manager__user__username', 'event__title')
    ordering = ('-created_at',)
    readonly_fields = ('assignment_id', 'created_at', 'updated_at', 'accepted_at', 'completed_at')
    fieldsets = (
        ('Assignment Info', {
            'fields': ('assignment_id', 'user', 'manager', 'status'),
            'description': 'Basic assignment information.'
        }),
        ('Event Context', {
            'fields': ('event', 'event_type', 'expected_guests', 'budget_range'),
            'description': 'Event details for the assignment.'
        }),
        ('Assignment Details', {
            'fields': ('assignment_reason', 'special_requirements'),
            'description': 'Why the assignment was made and special requirements.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'accepted_at', 'completed_at'),
            'description': 'Assignment timeline (read-only).'
        }),
    )

@admin.register(ManagerNote)
class ManagerNoteAdmin(admin.ModelAdmin):
    list_display = ('manager', 'author', 'title', 'note_type', 'is_important', 'created_at')
    list_filter = ('note_type', 'is_important', 'is_private', 'created_at')
    search_fields = ('manager__user__username', 'author__username', 'title', 'content')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Note Info', {
            'fields': ('manager', 'author', 'title', 'note_type'),
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
