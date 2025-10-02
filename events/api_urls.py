from django.urls import path
from . import api_views

app_name = 'events_api'

urlpatterns = [
    path('events/', api_views.EventListView.as_view(), name='event_list'),
    path('events/<int:pk>/', api_views.EventDetailView.as_view(), name='event_detail'),
] 