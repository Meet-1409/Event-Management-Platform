from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from datetime import timedelta
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.db.models import Q
from . import role_required
from events.models import Event, Registration
from payments.models import Payment

def home(request):
    """Home page view"""
    return render(request, 'home.html')

def register_view(request):
    """User registration view"""
    from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
    
    if request.user.is_authenticated:
        # Redirect based on user type
        if request.user.user_type == 'user':
            return redirect('users:dashboard')
        elif request.user.user_type == 'manager':
            return redirect('users:manager_dashboard')
        elif request.user.user_type == 'admin':
            return redirect('users:admin_dashboard')
        else:
            return redirect('home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Account created successfully! Welcome, {user.get_full_name()}!')
            
            # Redirect based on user type
            if user.user_type == 'user':
                return redirect('users:dashboard')
            elif user.user_type == 'manager':
                return redirect('users:manager_dashboard')
            elif user.user_type == 'admin':
                return redirect('users:admin_dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    """User login view"""
    from django.contrib.auth.forms import AuthenticationForm
    
    if request.user.is_authenticated:
        # Redirect based on user type
        if request.user.user_type == 'user':
            return redirect('users:dashboard')
        elif request.user.user_type == 'manager':
            return redirect('users:manager_dashboard')
        elif request.user.user_type == 'admin':
            return redirect('users:admin_dashboard')
        else:
            return redirect('home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, f'Welcome back, {user.get_full_name()}!')
                
                # Redirect based on user type
                if user.user_type == 'user':
                    next_url = request.GET.get('next', 'users:dashboard')
                elif user.user_type == 'manager':
                    next_url = request.GET.get('next', 'users:manager_dashboard')
                elif user.user_type == 'admin':
                    next_url = request.GET.get('next', 'users:admin_dashboard')
                else:
                    next_url = request.GET.get('next', 'home')
                
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')

@login_required
def profile_view(request):
    """User profile view"""
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserChangeForm(instance=request.user)
    
    context = {
        'form': form,
        'user': request.user,
    }
    return render(request, 'users/profile.html', context)

@login_required
def change_password(request):
    """Change password view"""
    from django.contrib.auth.forms import PasswordChangeForm
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # update_session_auth_hash(request, user) # This line was removed from imports, so it's removed here.
            messages.success(request, 'Your password was successfully updated!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'users/change_password.html', {'form': form})

@role_required(['user'])
def dashboard_view(request):
    """User dashboard view"""
    from . import dashboard_views
    return dashboard_views.dashboard(request)

@role_required(['user'])
def my_events(request):
    """User's events view"""
    user = request.user
    events = Event.objects.filter(organizer=user).order_by('-created_at')
    
    context = {
        'events': events,
        'user': user,
    }
    return render(request, 'users/my_events.html', context)

@role_required(['user'])
def my_bookings(request):
    """User's bookings view"""
    from django.core.paginator import Paginator
    
    user = request.user
    # Get bookings by email since Registration model uses email field
    bookings = Registration.objects.filter(email=user.email).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(bookings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'bookings': page_obj,
        'total_bookings': bookings.count(),
        'user': user,
    }
    return render(request, 'users/my_bookings.html', context)

@role_required(['user'])
def my_payments(request):
    """User's payments view"""
    user = request.user
    payments = Payment.objects.filter(user=user).order_by('-created_at')
    
    # Calculate payment statistics
    total_paid = sum(payment.amount for payment in payments if payment.status == 'completed')
    pending_payments = payments.filter(status='pending').count()
    completed_payments = payments.filter(status='completed').count()
    
    context = {
        'payments': payments,
        'user': user,
        'total_paid': total_paid,
        'pending_payments': pending_payments,
        'completed_payments': completed_payments,
    }
    return render(request, 'users/my_payments.html', context)

@role_required(['admin'])
def admin_dashboard(request):
    """Admin dashboard view"""
    from . import dashboard_views
    return dashboard_views.admin_dashboard(request)

@role_required(['manager'])
def manager_dashboard(request):
    """Manager dashboard view"""
    from . import dashboard_views
    return dashboard_views.manager_dashboard(request)

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_otp_sms(phone_number, otp):
    """Send OTP via SMS (placeholder for actual SMS service)"""
    # This would integrate with actual SMS service like Twilio, AWS SNS, etc.
    # For now, we'll simulate SMS sending
    print(f"SMS sent to {phone_number}: Your OTP is {otp}")
    return True

def forgot_password(request):
    """Handle forgot password with OTP"""
    if request.method == 'POST':
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        
        try:
            if email:
                user = CustomUser.objects.get(email=email)
            elif phone:
                user = CustomUser.objects.get(phone=phone)
            else:
                messages.error(request, 'Please provide either email or phone number')
                return render(request, 'users/forgot_password.html')
            
            # Generate OTP
            otp = generate_otp()
            
            # Store OTP in session with expiry
            request.session['reset_otp'] = otp
            request.session['reset_user_id'] = user.id
            request.session['reset_expiry'] = (timezone.now() + timedelta(minutes=5)).isoformat()
            
            # Send OTP via SMS if phone provided, otherwise email
            if phone:
                send_otp_sms(phone, otp)
                messages.success(request, f'OTP sent to {phone}')
            else:
                # Send OTP via email
                subject = 'Password Reset OTP'
                message = f'Your OTP for password reset is: {otp}\n\nThis OTP is valid for 5 minutes.'
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
                messages.success(request, f'OTP sent to {email}')
            
            return redirect('users:verify_otp')
            
        except CustomUser.DoesNotExist:
            messages.error(request, 'No user found with the provided email/phone')
    
    return render(request, 'users/forgot_password.html')

def verify_otp(request):
    """Verify OTP for password reset"""
    if request.method == 'POST':
        otp = request.POST.get('otp')
        stored_otp = request.session.get('reset_otp')
        user_id = request.session.get('reset_user_id')
        expiry = request.session.get('reset_expiry')
        
        if not all([otp, stored_otp, user_id, expiry]):
            messages.error(request, 'Invalid reset session')
            return redirect('users:forgot_password')
        
        # Check if OTP is expired
        expiry_time = timezone.datetime.fromisoformat(expiry)
        if timezone.now() > expiry_time:
            messages.error(request, 'OTP has expired. Please request a new one.')
            return redirect('users:forgot_password')
        
        # Verify OTP
        if otp == stored_otp:
            user = get_object_or_404(CustomUser, id=user_id)
            request.session['reset_verified'] = True
            return redirect('users:reset_password')
        else:
            messages.error(request, 'Invalid OTP')
    
    return render(request, 'users/verify_otp.html')

def reset_password(request):
    """Reset password after OTP verification"""
    if not request.session.get('reset_verified'):
        messages.error(request, 'Please verify OTP first')
        return redirect('users:forgot_password')
    
    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'users/reset_password.html')
        
        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long')
            return render(request, 'users/reset_password.html')
        
        # Update password
        user_id = request.session.get('reset_user_id')
        user = get_object_or_404(CustomUser, id=user_id)
        user.set_password(password1)
        user.save()
        
        # Clear session
        for key in ['reset_otp', 'reset_user_id', 'reset_expiry', 'reset_verified']:
            request.session.pop(key, None)
        
        messages.success(request, 'Password reset successfully! Please login with your new password.')
        return redirect('users:login')
    
    return render(request, 'users/reset_password.html')

@login_required
def my_bookings(request):
    """User's bookings page"""
    bookings = Registration.objects.filter(email=request.user.email).order_by('-created_at')
    
    context = {
        'bookings': bookings,
    }
    return render(request, 'users/my_bookings.html', context)
