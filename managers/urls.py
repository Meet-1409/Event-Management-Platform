from django.urls import path
from . import views

app_name = 'managers'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('', views.manager_list, name='manager_list'),
    path('contact/<int:manager_id>/', views.contact_manager, name='contact_manager'),
    path('verification/', views.manager_verification, name='manager_verification'),
    path('verify/<int:manager_id>/', views.verify_manager, name='verify_manager'),
    path('<slug:manager_slug>/', views.manager_detail, name='manager_detail'),
] 