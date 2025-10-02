from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('calendar/', views.calendar_view, name='calendar_view'),
    path('add/', views.create_event, name='add_event'),
    path('edit/<int:event_id>/', views.edit_event, name='edit_event'),
    path('delete/<int:event_id>/', views.delete_event, name='delete_event'),
    path('detail/<int:event_id>/', views.event_detail, name='event_detail'),
    path('register/<int:event_id>/', views.event_registration, name='event_registration'),
    path('registration-success/<int:booking_id>/', views.registration_success, name='registration_success'),
    path('gallery/<int:event_id>/', views.event_gallery, name='event_gallery'),
    path('categories/', views.event_categories, name='event_categories'),
    path('adventure/', views.adventure_events, name='adventure_events'),
    path('movie/', views.movie_events, name='movie_events'),
    path('music/', views.music_events, name='music_events'),
    path('cooking/', views.cooking_events, name='cooking_events'),
    path('coding/', views.coding_events, name='coding_events'),
    path('sports/', views.sports_events, name='sports_events'),
    path('booking/<int:event_id>/', views.booking_page, name='booking_page'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('invoice/<int:booking_id>/', views.generate_invoice, name='generate_invoice'),
    path('reviews/<int:event_id>/', views.reviews_section, name='reviews_section'),
    # New review system URLs
    path('submit-review/<int:event_id>/', views.submit_review, name='submit_review'),
    path('edit-review/<int:review_id>/', views.edit_review, name='edit_review'),
    path('delete-review/<int:review_id>/', views.delete_review, name='delete_review'),
    path('get-reviews/<int:event_id>/', views.get_reviews, name='get_reviews'),
] 