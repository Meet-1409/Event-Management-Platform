from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import CustomUser, UserRoleRequest


@login_required
def admin_role_requests(request):
    """Admin dashboard to view and manage role requests"""
    if not request.user.is_admin:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('users:dashboard')
    
    # Get pending role requests
    pending_requests = UserRoleRequest.objects.filter(status='pending').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(pending_requests, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'pending_count': pending_requests.count(),
    }
    
    return render(request, 'users/admin_role_requests.html', context)


@login_required
def approve_role_request(request, request_id):
    """Approve a role request"""
    if not request.user.is_admin:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('users:dashboard')
    
    role_request = get_object_or_404(UserRoleRequest, id=request_id, status='pending')
    
    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        role_request.approve(request.user, notes)
        
        messages.success(
            request, 
            f'Role request approved! {role_request.user.get_full_name()} is now a {role_request.get_requested_role_display()}.'
        )
        
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({
                'status': 'success',
                'message': 'Role request approved successfully'
            })
        
        return redirect('users:admin_role_requests')
    
    context = {
        'role_request': role_request,
    }
    
    return render(request, 'users/admin_approve_request.html', context)


@login_required
def reject_role_request(request, request_id):
    """Reject a role request"""
    if not request.user.is_admin:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('users:dashboard')
    
    role_request = get_object_or_404(UserRoleRequest, id=request_id, status='pending')
    
    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        role_request.reject(request.user, notes)
        
        messages.success(
            request, 
            f'Role request rejected for {role_request.user.get_full_name()}.'
        )
        
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({
                'status': 'success',
                'message': 'Role request rejected'
            })
        
        return redirect('users:admin_role_requests')
    
    context = {
        'role_request': role_request,
    }
    
    return render(request, 'users/admin_reject_request.html', context)


@login_required
def admin_user_management(request):
    """Admin dashboard for user management"""
    if not request.user.is_admin:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('users:dashboard')
    
    # Get all users
    users = CustomUser.objects.all().order_by('-date_joined')
    
    # Filter options
    user_type = request.GET.get('type', '')
    if user_type:
        users = users.filter(user_type=user_type)
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    stats = {
        'total_users': CustomUser.objects.count(),
        'regular_users': CustomUser.objects.filter(user_type='user').count(),
        'managers': CustomUser.objects.filter(user_type='manager').count(),
        'admins': CustomUser.objects.filter(user_type='admin').count(),
        'pending_requests': UserRoleRequest.objects.filter(status='pending').count(),
    }
    
    context = {
        'page_obj': page_obj,
        'stats': stats,
        'current_filter': user_type,
    }
    
    return render(request, 'users/admin_user_management.html', context)
