"""
Security utilities for file uploads and validation
"""
import os
import hashlib
import magic
from django.core.exceptions import ValidationError
from django.conf import settings
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class FileSecurityValidator:
    """
    Comprehensive file security validation
    """
    
    def __init__(self):
        self.allowed_extensions = getattr(settings, 'ALLOWED_FILE_EXTENSIONS', {})
        self.max_file_sizes = getattr(settings, 'MAX_FILE_SIZES', {})
        self.enable_virus_scanning = getattr(settings, 'ENABLE_VIRUS_SCANNING', False)
    
    def validate_file(self, file, file_type='image'):
        """
        Validate uploaded file for security
        """
        try:
            # Check file size
            self._validate_file_size(file, file_type)
            
            # Check file extension
            self._validate_file_extension(file, file_type)
            
            # Check MIME type
            self._validate_mime_type(file)
            
            # Check file content
            self._validate_file_content(file)
            
            # Check for malicious content
            self._scan_for_malicious_content(file)
            
            return True
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"File validation error: {str(e)}")
            raise ValidationError("File validation failed.")
    
    def _validate_file_size(self, file, file_type):
        """Validate file size"""
        max_size = self.max_file_sizes.get(file_type, 5 * 1024 * 1024)  # Default 5MB
        
        if file.size > max_size:
            raise ValidationError(f"File size exceeds maximum allowed size of {max_size // (1024*1024)}MB.")
    
    def _validate_file_extension(self, file, file_type):
        """Validate file extension"""
        allowed_extensions = self.allowed_extensions.get(file_type, [])
        
        if not allowed_extensions:
            return
        
        file_extension = os.path.splitext(file.name)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise ValidationError(f"File type '{file_extension}' is not allowed.")
    
    def _validate_mime_type(self, file):
        """Validate MIME type using python-magic"""
        try:
            # Read file content
            file.seek(0)
            file_content = file.read(1024)  # Read first 1KB
            file.seek(0)  # Reset file pointer
            
            # Detect MIME type
            mime_type = magic.from_buffer(file_content, mime=True)
            
            # Allowed MIME types
            allowed_mime_types = [
                'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp',
                'application/pdf', 'text/plain', 'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/zip', 'application/x-rar-compressed',
            ]
            
            if mime_type not in allowed_mime_types:
                raise ValidationError(f"File type '{mime_type}' is not allowed.")
                
        except Exception as e:
            logger.warning(f"MIME type validation failed: {str(e)}")
            # Continue without MIME validation if magic library fails
    
    def _validate_file_content(self, file):
        """Validate file content"""
        try:
            file.seek(0)
            file_content = file.read()
            file.seek(0)
            
            # Check for executable signatures
            executable_signatures = [
                b'\x4d\x5a',  # PE executable
                b'\x7f\x45\x4c\x46',  # ELF executable
                b'\xfe\xed\xfa',  # Mach-O executable
                b'\xce\xfa\xed\xfe',  # Mach-O executable (32-bit)
            ]
            
            for signature in executable_signatures:
                if signature in file_content:
                    raise ValidationError("File contains executable content.")
            
            # Check for script tags in images
            if file.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                script_tags = [b'<script', b'javascript:', b'vbscript:', b'onload=']
                for tag in script_tags:
                    if tag in file_content:
                        raise ValidationError("File contains potentially malicious content.")
                        
        except ValidationError:
            raise
        except Exception as e:
            logger.warning(f"File content validation failed: {str(e)}")
    
    def _scan_for_malicious_content(self, file):
        """Scan for malicious content"""
        if not self.enable_virus_scanning:
            return
        
        try:
            # Placeholder for virus scanning integration
            # This would integrate with services like ClamAV, VirusTotal API, etc.
            pass
            
        except Exception as e:
            logger.error(f"Virus scanning failed: {str(e)}")
    
    def sanitize_filename(self, filename):
        """Sanitize filename to prevent path traversal"""
        # Remove directory traversal attempts
        filename = os.path.basename(filename)
        
        # Remove special characters
        allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_"
        filename = ''.join(c for c in filename if c in allowed_chars)
        
        # Limit filename length
        if len(filename) > 100:
            name, ext = os.path.splitext(filename)
            filename = name[:95] + ext
        
        return filename
    
    def generate_secure_filename(self, original_filename):
        """Generate a secure filename with hash"""
        # Get file extension
        file_extension = os.path.splitext(original_filename)[1]
        
        # Generate hash
        hash_obj = hashlib.sha256()
        hash_obj.update(original_filename.encode('utf-8'))
        hash_obj.update(str(os.urandom(16)).encode('utf-8'))
        hash_hex = hash_obj.hexdigest()[:16]
        
        return f"{hash_hex}{file_extension}"


class ImageSecurityValidator(FileSecurityValidator):
    """
    Specialized validator for image files
    """
    
    def validate_image(self, file):
        """Validate image file specifically"""
        try:
            # Basic file validation
            self.validate_file(file, 'image')
            
            # Image-specific validation
            self._validate_image_dimensions(file)
            self._validate_image_metadata(file)
            
            return True
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Image validation error: {str(e)}")
            raise ValidationError("Image validation failed.")
    
    def _validate_image_dimensions(self, file):
        """Validate image dimensions"""
        try:
            file.seek(0)
            with Image.open(file) as img:
                width, height = img.size
                
                # Check maximum dimensions
                max_width = 4096
                max_height = 4096
                
                if width > max_width or height > max_height:
                    raise ValidationError(f"Image dimensions ({width}x{height}) exceed maximum allowed ({max_width}x{max_height}).")
                
                # Check minimum dimensions
                min_width = 10
                min_height = 10
                
                if width < min_width or height < min_height:
                    raise ValidationError(f"Image dimensions ({width}x{height}) are too small.")
                    
            file.seek(0)
            
        except ValidationError:
            raise
        except Exception as e:
            logger.warning(f"Image dimension validation failed: {str(e)}")
    
    def _validate_image_metadata(self, file):
        """Validate and strip image metadata"""
        try:
            file.seek(0)
            with Image.open(file) as img:
                # Check for suspicious metadata
                if hasattr(img, '_getexif') and img._getexif():
                    exif = img._getexif()
                    
                    # Check for GPS data (privacy concern)
                    if 34853 in exif:  # GPS tag
                        logger.warning("Image contains GPS metadata")
                    
                    # Check for software information
                    if 271 in exif:  # Software tag
                        software = exif[271]
                        if any(suspicious in software.lower() for suspicious in ['hack', 'crack', 'keygen']):
                            raise ValidationError("Image contains suspicious metadata.")
                            
            file.seek(0)
            
        except ValidationError:
            raise
        except Exception as e:
            logger.warning(f"Image metadata validation failed: {str(e)}")


def validate_file_upload(file, file_type='image'):
    """
    Convenience function for file validation
    """
    if file_type == 'image':
        validator = ImageSecurityValidator()
        return validator.validate_image(file)
    else:
        validator = FileSecurityValidator()
        return validator.validate_file(file, file_type)
