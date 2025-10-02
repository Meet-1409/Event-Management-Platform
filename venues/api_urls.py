from django.urls import path
from . import api_views

app_name = 'venues_api'

urlpatterns = [
    # Venue API endpoints
    path('venues/', api_views.VenueListView.as_view(), name='venue_list'),
    path('venues/<slug:slug>/', api_views.VenueDetailView.as_view(), name='venue_detail'),
    path('venues/search/', api_views.VenueSearchView.as_view(), name='venue_search'),
    
    # Enhanced Gallery API
path('venues/<slug:slug>/gallery-enhanced/', api_views.VenueGalleryEnhancedView.as_view(), name='venue_gallery_enhanced'),
    path('venues/<slug:slug>/tour/hotspots/', api_views.TourHotspotsView.as_view(), name='tour_hotspots'),
    
    # Venue availability and booking
    path('venues/<slug:slug>/availability/', api_views.VenueAvailabilityView.as_view(), name='venue_availability'),
    path('venues/<slug:slug>/book/', api_views.VenueBookingView.as_view(), name='venue_booking'),
    path('venues/<slug:slug>/packages/', api_views.VenuePackagesView.as_view(), name='venue_packages'),
    
    # Venue reviews
    path('venues/<slug:slug>/reviews/', api_views.VenueReviewsView.as_view(), name='venue_reviews'),
    path('venues/<slug:slug>/reviews/create/', api_views.CreateReviewView.as_view(), name='create_review'),
    
    # Categories
    path('categories/', api_views.VenueCategoryListView.as_view(), name='category_list'),
    path('categories/<slug:slug>/venues/', api_views.CategoryVenuesView.as_view(), name='category_venues'),
] 