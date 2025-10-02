from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('dashboard/', views.analytics_dashboard, name='dashboard'),
    path('api/dashboard-data/', views.get_dashboard_data, name='dashboard_data'),
    path('api/event-analytics/', views.get_event_analytics, name='event_analytics'),
    path('api/revenue-analytics/', views.get_revenue_analytics, name='revenue_analytics'),
    path('export/', views.export_analytics, name='export_analytics'),
] 