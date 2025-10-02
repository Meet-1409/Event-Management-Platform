from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from users.models import CustomUser
from users.forms import CustomUserCreationForm

class AdminCreationForm(CustomUserCreationForm):
    class Meta(CustomUserCreationForm.Meta):
        pass

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'admin'
        if commit:
            user.save()
        return user

class AdminAuthenticationForm(AuthenticationForm):
    pass 