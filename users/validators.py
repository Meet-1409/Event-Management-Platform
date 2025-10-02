"""
Custom password validators for enhanced security
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class UppercaseValidator:
    """
    Validate that the password contains at least one uppercase letter.
    """
    
    def validate(self, password, user=None):
        if not any(c.isupper() for c in password):
            raise ValidationError(
                _("This password must contain at least one uppercase letter."),
                code='password_no_upper',
            )
    
    def get_help_text(self):
        return _("Your password must contain at least one uppercase letter.")


class LowercaseValidator:
    """
    Validate that the password contains at least one lowercase letter.
    """
    
    def validate(self, password, user=None):
        if not any(c.islower() for c in password):
            raise ValidationError(
                _("This password must contain at least one lowercase letter."),
                code='password_no_lower',
            )
    
    def get_help_text(self):
        return _("Your password must contain at least one lowercase letter.")


class SpecialCharValidator:
    """
    Validate that the password contains at least one special character.
    """
    
    def validate(self, password, user=None):
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            raise ValidationError(
                _("This password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)."),
                code='password_no_special',
            )
    
    def get_help_text(self):
        return _("Your password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?).")


class NumberValidator:
    """
    Validate that the password contains at least one number.
    """
    
    def validate(self, password, user=None):
        if not any(c.isdigit() for c in password):
            raise ValidationError(
                _("This password must contain at least one number."),
                code='password_no_number',
            )
    
    def get_help_text(self):
        return _("Your password must contain at least one number.")


class NoCommonWordsValidator:
    """
    Validate that the password doesn't contain common words.
    """
    
    COMMON_WORDS = [
        'password', 'admin', 'user', 'login', 'welcome', 'hello', 'world',
        'test', 'demo', 'sample', 'example', 'default', 'guest', 'public',
        'private', 'secret', 'key', 'token', 'session', 'cookie', 'auth'
    ]
    
    def validate(self, password, user=None):
        password_lower = password.lower()
        for word in self.COMMON_WORDS:
            if word in password_lower:
                raise ValidationError(
                    _("This password contains common words and is not secure."),
                    code='password_common_word',
                )
    
    def get_help_text(self):
        return _("Your password cannot contain common words like 'password', 'admin', etc.")


class NoPersonalInfoValidator:
    """
    Validate that the password doesn't contain personal information.
    """
    
    def validate(self, password, user=None):
        if user:
            # Check against username
            if user.username and user.username.lower() in password.lower():
                raise ValidationError(
                    _("This password cannot contain your username."),
                    code='password_username',
                )
            
            # Check against email
            if user.email and user.email.split('@')[0].lower() in password.lower():
                raise ValidationError(
                    _("This password cannot contain your email address."),
                    code='password_email',
                )
            
            # Check against first and last name
            if user.first_name and user.first_name.lower() in password.lower():
                raise ValidationError(
                    _("This password cannot contain your first name."),
                    code='password_first_name',
                )
            
            if user.last_name and user.last_name.lower() in password.lower():
                raise ValidationError(
                    _("This password cannot contain your last name."),
                    code='password_last_name',
                )
    
    def get_help_text(self):
        return _("Your password cannot contain your username, email, or name.")


class NoRepeatedCharsValidator:
    """
    Validate that the password doesn't have too many repeated characters.
    """
    
    def validate(self, password, user=None):
        # Check for repeated characters (more than 3 consecutive)
        for i in range(len(password) - 3):
            if password[i] == password[i+1] == password[i+2] == password[i+3]:
                raise ValidationError(
                    _("This password cannot have more than 3 consecutive identical characters."),
                    code='password_repeated_chars',
                )
    
    def get_help_text(self):
        return _("Your password cannot have more than 3 consecutive identical characters.")


class NoSequentialCharsValidator:
    """
    Validate that the password doesn't contain sequential characters.
    """
    
    def validate(self, password, user=None):
        # Check for sequential characters (like abc, 123, etc.)
        for i in range(len(password) - 2):
            if (ord(password[i+1]) == ord(password[i]) + 1 and 
                ord(password[i+2]) == ord(password[i]) + 2):
                raise ValidationError(
                    _("This password cannot contain sequential characters."),
                    code='password_sequential',
                )
    
    def get_help_text(self):
        return _("Your password cannot contain sequential characters like 'abc' or '123'.")
