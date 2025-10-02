from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import AdminCreationForm, AdminAuthenticationForm
from users.models import CustomUser
from django.contrib.auth.decorators import login_required
from users import role_required

def login_view(request):
    if request.user.is_authenticated:
        return redirect('users:admin_dashboard')
    if request.method == 'POST':
        form = AdminAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.user_type == 'admin':
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('users:admin_dashboard')
            else:
                messages.error(request, 'Invalid credentials or not an admin account.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminAuthenticationForm()
    return render(request, 'admins/login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('admins:dashboard')
    if request.method == 'POST':
        form = AdminCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome, {user.username}!')
            return redirect('admins:dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminCreationForm()
    return render(request, 'admins/register.html', {'form': form})

# Removed dashboard_view as /admins/dashboard/ is deprecated 