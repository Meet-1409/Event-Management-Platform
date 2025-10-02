from django.core.management.base import BaseCommand
from events.models import Event

class Command(BaseCommand):
    help = 'Add sample images to gallery events'

    def handle(self, *args, **options):
        self.stdout.write('Adding sample images to gallery events...')
        
        # Sample image URLs for different event types
        image_urls = {
            'Sports': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=300&fit=crop',
            'Corporate': 'https://images.unsplash.com/photo-1511578314322-379afb476865?w=400&h=300&fit=crop',
            'Wedding': 'https://images.unsplash.com/photo-1519741497674-611481863552?w=400&h=300&fit=crop',
            'Birthday': 'https://images.unsplash.com/photo-1515187029135-18ee286d815b?w=400&h=300&fit=crop',
            'Music': 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=400&h=300&fit=crop',
            'Cultural': 'https://images.unsplash.com/photo-1511795409834-ef04bbd61622?w=400&h=300&fit=crop',
        }
        
        # Get events without images
        events = Event.objects.filter(
            status='completed',
            event_image__isnull=True
        )
        
        updated_count = 0
        for event in events:
            event_type = event.event_type.name if event.event_type else 'Corporate'
            image_url = image_urls.get(event_type, image_urls['Corporate'])
            
            # Set the image URL directly (not as a file upload)
            event.event_image = image_url
            event.save()
            updated_count += 1
            self.stdout.write(f'Added image to: {event.title}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully added images to {updated_count} events!')
        )
