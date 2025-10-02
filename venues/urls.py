from django.urls import path
from . import views

app_name = 'venues'

urlpatterns = [
    # Venue listing and search
    path('', views.venue_list, name='venue_list'),
    path('search/', views.venue_search, name='venue_search'),
    path('category/<slug:category_slug>/', views.venue_list_by_category, name='venue_list_by_category'),
    
    # Venue details
    path('<slug:venue_slug>/', views.venue_detail, name='venue_detail'),
    path('<slug:venue_slug>/gallery-enhanced/', views.venue_gallery_enhanced, name='venue_gallery_enhanced'),
    path('<slug:venue_slug>/gallery/', views.venue_gallery, name='venue_gallery'),
    path('<slug:venue_slug>/reviews/', views.venue_reviews, name='venue_reviews'),
    
    # Venue booking
    path('<slug:venue_slug>/book/', views.venue_booking, name='venue_booking'),
    path('<slug:venue_slug>/availability/', views.venue_availability, name='venue_availability'),
    path('<slug:venue_slug>/packages/', views.venue_packages, name='venue_packages'),
] 