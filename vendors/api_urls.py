from django.urls import path
from . import api_views

app_name = 'vendors_api'

urlpatterns = [
    path('vendors/', api_views.VendorListView.as_view(), name='vendor_list'),
    path('vendors/<slug:slug>/', api_views.VendorDetailView.as_view(), name='vendor_detail'),
] 