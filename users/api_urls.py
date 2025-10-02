from django.urls import path
from . import api_views

app_name = 'users_api'

urlpatterns = [
    # Authentication API
    path('auth/register/', api_views.UserRegistrationView.as_view(), name='register'),
    path('auth/login/', api_views.UserLoginView.as_view(), name='login'),
    path('auth/logout/', api_views.UserLogoutView.as_view(), name='logout'),
    path('auth/profile/', api_views.UserProfileView.as_view(), name='profile'),
    
    # User management API
    path('users/', api_views.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', api_views.UserDetailView.as_view(), name='user_detail'),
    path('users/profile/update/', api_views.ProfileUpdateView.as_view(), name='profile_update'),
] 