from django.urls import path
from . import api_views

app_name = 'managers_api'

urlpatterns = [
    path('managers/', api_views.ManagerListView.as_view(), name='manager_list'),
    path('managers/<slug:slug>/', api_views.ManagerDetailView.as_view(), name='manager_detail'),
] 