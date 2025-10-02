from django.contrib import admin
from .models import Event, EventType, Registration, EventReview

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'venue', 'start_date', 'organizer', 'status')
    list_filter = ('event_type', 'venue', 'status')
    search_fields = ('title', 'venue__name', 'organizer__username')
    ordering = ('-start_date',)
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'event_type', 'venue', 'organizer', 'status'),
            'description': 'Fill in the main details of the event.'
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date', 'start_time', 'end_time'),
            'description': 'Set when the event starts and ends.'
        }),
        ('Details', {
            'fields': ('description', 'expected_guests', 'theme'),
            'description': 'Add a description and any special theme.'
        }),
    )

@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('event', 'name', 'email', 'phone', 'guest_count', 'source', 'terms_accepted', 'created_at')
    search_fields = ('name', 'email', 'event__title', 'phone', 'special_requirements')
    list_filter = ('event', 'source', 'terms_accepted', 'created_at', 'event__event_type')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Registration Information', {
            'fields': ('event', 'name', 'email', 'phone', 'guest_count')
        }),
        ('Additional Details', {
            'fields': ('special_requirements', 'source', 'terms_accepted'),
            'description': 'Additional information provided by the registrant'
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('event', 'event__venue')

@admin.register(EventReview)
class EventReviewAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'rating', 'title', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'created_at', 'event__event_type')
    search_fields = ('event__title', 'user__username', 'user__email', 'title', 'comment')
    ordering = ('-created_at',)
    list_editable = ('is_approved',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Review Information', {
            'fields': ('event', 'user', 'rating', 'title', 'comment')
        }),
        ('Moderation', {
            'fields': ('is_approved',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_reviews', 'reject_reviews']
    
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} review(s) have been approved.')
    approve_reviews.short_description = "Approve selected reviews"
    
    def reject_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} review(s) have been rejected.')
    reject_reviews.short_description = "Reject selected reviews"
