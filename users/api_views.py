from django.http import JsonResponse
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import CustomUser
from .forms import CustomUserCreationForm
import json

@method_decorator(csrf_exempt, name='dispatch')
class UserRegistrationView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            form = CustomUserCreationForm(data)
            if form.is_valid():
                user = form.save()
                return JsonResponse({
                    "success": True,
                    "message": "User registered successfully",
                    "user_id": user.id,
                    "email": user.email
                })
            else:
                return JsonResponse({
                    "success": False,
                    "errors": form.errors
                })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

@method_decorator(csrf_exempt, name='dispatch')
class UserLoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                return JsonResponse({
                    "success": True,
                    "message": "Login successful",
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "name": user.get_full_name(),
                        "user_type": user.user_type
                    }
                })
            else:
                return JsonResponse({"success": False, "error": "Invalid credentials"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

@method_decorator(csrf_exempt, name='dispatch')
class UserLogoutView(View):
    def post(self, request):
        logout(request)
        return JsonResponse({"success": True, "message": "Logged out successfully"})

@method_decorator(login_required, name='dispatch')
class UserProfileView(View):
    def get(self, request):
        user = request.user
        return JsonResponse({
            "success": True,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone_number": user.phone_number,
                "user_type": user.user_type,
                "date_joined": user.date_joined.isoformat(),
                "profile_completion": user.get_profile_completion_percentage()
            }
        })

class UserListView(View):
    def get(self, request):
        users = CustomUser.objects.filter(is_active=True).order_by('-date_joined')
        paginator = Paginator(users, 20)
        page = paginator.get_page(request.GET.get('page', 1))
        
        return JsonResponse({
            "success": True,
            "users": [{
                "id": user.id,
                "email": user.email,
                "name": user.get_full_name(),
                "user_type": user.user_type,
                "date_joined": user.date_joined.isoformat()
            } for user in page],
            "pagination": {
                "page": page.number,
                "pages": paginator.num_pages,
                "has_next": page.has_next(),
                "has_previous": page.has_previous()
            }
        })

class UserDetailView(View):
    def get(self, request, pk):
        try:
            user = CustomUser.objects.get(id=pk)
            return JsonResponse({
                "success": True,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "user_type": user.user_type,
                    "date_joined": user.date_joined.isoformat(),
                    "is_active": user.is_active
                }
            })
        except CustomUser.DoesNotExist:
            return JsonResponse({"success": False, "error": "User not found"})

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            user = request.user
            
            # Update allowed fields
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'phone_number' in data:
                user.phone_number = data['phone_number']
                
            user.save()
            
            return JsonResponse({
                "success": True,
                "message": "Profile updated successfully"
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})