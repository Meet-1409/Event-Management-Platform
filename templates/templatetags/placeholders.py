from django import template
import hashlib

register = template.Library()

@register.filter
def placeholder_for(category, index=0):
    """
    Generate unique, category-appropriate Unsplash placeholder images
    
    Usage: {{ 'sports'|placeholder_for:forloop.counter0 }}
    """
    
    # Category mappings to appropriate Unsplash search terms
    category_mappings = {
        'festival': 'festival-celebration-colorful',
        'sports': 'sports-stadium-action',
        'music': 'concert-stage-lights',
        'cooking': 'chef-kitchen-food',
        'coding': 'programming-computer-code',
        'movies': 'cinema-theater-screen',
        'wedding': 'wedding-ceremony-celebration',
        'conference': 'business-conference-meeting',
        'party': 'party-celebration-balloons',
        'outdoor': 'outdoor-adventure-nature',
        'workshop': 'workshop-learning-education',
        'corporate': 'corporate-business-office',
        'cultural': 'cultural-traditional-art',
        'adventure': 'adventure-hiking-outdoor',
        'default': 'event-celebration-people'
    }
    
    # Get search term for category
    search_term = category_mappings.get(category.lower(), category_mappings['default'])
    
    # Create unique signature based on category and index
    signature = hashlib.md5(f"{category}-{index}".encode()).hexdigest()[:8]
    
    # Generate deterministic dimensions based on index
    width = 800
    height = 600
    
    # Create Unsplash URL with category-specific search and unique signature
    url = f"https://images.unsplash.com/photo-1{signature}?w={width}&h={height}&fit=crop&q=80&auto=format&{search_term}&sig={signature}"
    
    return url

@register.filter  
def placeholder_fallback(image_field, category):
    """
    Return image URL if exists, otherwise return category placeholder
    
    Usage: {{ event.event_image|placeholder_fallback:'sports' }}
    """
    if image_field and hasattr(image_field, 'url'):
        return image_field.url
    return placeholder_for(category, 0)

@register.simple_tag
def unique_placeholder(category, index=0):
    """
    Simple tag version for more complex usage
    
    Usage: {% unique_placeholder 'sports' forloop.counter0 %}
    """
    return placeholder_for(category, index)

@register.filter
def event_category_image(event, index=0):
    """
    Get appropriate placeholder based on event type
    
    Usage: {{ event|event_category_image:forloop.counter0 }}
    """
    if event.event_image and hasattr(event.event_image, 'url'):
        return event.event_image.url
        
    # Map event types to categories
    event_type_mapping = {
        'Sports': 'sports',
        'Music': 'music', 
        'Workshop': 'workshop',
        'Cultural Festival': 'cultural',
        'Adventure': 'adventure',
        'Technology': 'coding',
        'Entertainment': 'party',
        'Corporate': 'corporate',
        'Wedding': 'wedding',
        'Conference': 'conference'
    }
    
    category = event_type_mapping.get(event.event_type.name, 'festival')
    return placeholder_for(category, index)

@register.filter
def venue_category_image(venue, index=0):
    """
    Get appropriate placeholder based on venue category
    
    Usage: {{ venue|venue_category_image:forloop.counter0 }}
    """
    if venue.main_image and hasattr(venue.main_image, 'image'):
        return venue.main_image.image.url
        
    # Map venue categories to placeholder categories  
    venue_type_mapping = {
        'Wedding': 'wedding',
        'Corporate': 'corporate',
        'Sports Complex': 'sports',
        'Conference Hall': 'conference',
        'Outdoor': 'outdoor',
        'Party Hall': 'party',
        'Cultural Center': 'cultural'
    }
    
    category = venue_type_mapping.get(venue.category.name, 'conference')
    return placeholder_for(category, index)
