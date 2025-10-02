from django.contrib import admin
from .models import Venue, VenueCategory

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'city', 'capacity_min', 'capacity_max', 'status')
    search_fields = ('name', 'city')
    list_filter = ('category', 'status')
    ordering = ('-created_at',)
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'category', 'status'),
            'description': 'Main details about the venue.'
        }),
        ('Location', {
            'fields': ('city', 'address'),
            'description': 'Where is the venue located?'
        }),
        ('Capacity', {
            'fields': ('capacity_min', 'capacity_max'),
            'description': 'How many people can the venue hold?'
        }),
    )

@admin.register(VenueCategory)
class VenueCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
