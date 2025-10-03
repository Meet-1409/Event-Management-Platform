from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from .models import CustomUser

class SimplePasswordField(forms.CharField):
    """Simplified password field with minimal validation"""
    widget = forms.PasswordInput
    strip = False
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget.attrs.update({
            'autocomplete': 'new-password',
            'class': 'form-control'
        })
    
    def validate(self, value):
        super().validate(value)
        if len(value) < 3:  # Only require minimum 3 characters
            raise ValidationError(
                'Password must be at least 3 characters long.',
                code='password_too_short',
            )

class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form with simplified password validation"""
    email = forms.EmailField(required=True, help_text='Required. Enter a valid email address.')
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    phone_number = forms.CharField(
        max_length=17, 
        required=True, 
        help_text='Required. Enter your phone number (e.g., +91-9876543210).',
        widget=forms.TextInput(attrs={'placeholder': '+91-9876543210'})
    )
    user_type = forms.ChoiceField(
        choices=CustomUser.USER_TYPE_CHOICES,
        initial='user',
        help_text='Select your account type. Manager and Admin accounts require approval.',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    password1 = SimplePasswordField(
        label="Password",
        help_text="Enter your password (minimum 3 characters)."
    )
    password2 = SimplePasswordField(
        label="Password confirmation",
        help_text="Enter the same password as before, for verification."
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'user_type', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data['phone_number']
        if commit:
            user.save()
        return user

class CustomUserChangeForm(UserChangeForm):
    """Custom user change form"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(
        max_length=17, 
        required=False,  # Make phone number optional
        widget=forms.TextInput(attrs={'placeholder': '+91-9876543210'})
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure form fields are properly initialized
        if self.instance and self.instance.pk:
            self.fields['first_name'].initial = self.instance.first_name
            self.fields['last_name'].initial = self.instance.last_name
            self.fields['email'].initial = self.instance.email
            self.fields['phone_number'].initial = self.instance.phone_number
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Basic phone number validation (allow various formats)
            import re
            if not re.match(r'^\+?[\d\s\-\(\)]{9,17}$', phone_number):
                raise forms.ValidationError('Enter a valid phone number.')
        return phone_number
    
    def save(self, commit=True):
        """Override save to ensure proper saving"""
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data.get('phone_number', '')
        
        if commit:
            user.save()
        return user 