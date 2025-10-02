from django.urls import path
from . import dashboard_views

app_name = 'dashboard'

urlpatterns = [
    # Main dashboard
    path('', dashboard_views.dashboard_home, name='home'),
    
    # User dashboard
    path('user/events/', dashboard_views.user_events, name='user_events'),
    path('user/bookings/', dashboard_views.user_bookings, name='user_bookings'),
    path('user/payments/', dashboard_views.user_payments, name='user_payments'),
    path('user/messages/', dashboard_views.user_messages, name='user_messages'),
    
    # Manager dashboard
    path('manager/', dashboard_views.manager_dashboard, name='manager_dashboard'),
    path('manager/clients/', dashboard_views.manager_clients, name='manager_clients'),
    path('manager/events/', dashboard_views.manager_events, name='manager_events'),
    path('manager/consultations/', dashboard_views.manager_consultations, name='manager_consultations'),
    path('manager/earnings/', dashboard_views.manager_earnings, name='manager_earnings'),
    
    # Admin dashboard
    path('admin/', dashboard_views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', dashboard_views.admin_users, name='admin_users'),
    path('admin/managers/', dashboard_views.admin_managers, name='admin_managers'),
    path('admin/venues/', dashboard_views.admin_venues, name='admin_venues'),
    path('admin/vendors/', dashboard_views.admin_vendors, name='admin_vendors'),
    path('admin/events/', dashboard_views.admin_events, name='admin_events'),
    path('admin/payments/', dashboard_views.admin_payments, name='admin_payments'),
    path('admin/reports/', dashboard_views.admin_reports, name='admin_reports'),
] 