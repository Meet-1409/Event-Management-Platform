from django import forms
from .models import Event, EventType, EventGuest, EventTimeline, EventChecklist, EventReview
from venues.models import Venue, VenuePackage

class EventCreationForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'event_type', 'start_date', 'end_date',
            'start_time', 'end_time', 'expected_guests', 'venue', 'venue_package',
            'total_budget', 'theme', 'special_requirements'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Event Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Event Description'}),
            'event_type': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'expected_guests': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'venue': forms.Select(attrs={'class': 'form-control'}),
            'venue_package': forms.Select(attrs={'class': 'form-control'}),
            'total_budget': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'theme': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Event Theme'}),
            'special_requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Special Requirements'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Filter venues based on user permissions
            self.fields['venue'].queryset = Venue.objects.filter(status='active')
            self.fields['venue_package'].queryset = VenuePackage.objects.all()
            # Only allow public event types (no private events like birthdays, weddings, corporate)
            self.fields['event_type'].queryset = EventType.objects.filter(
                is_active=True,
                name__in=['Sports', 'Sports Tournament', 'Workshop', 'Cultural Festival', 'Music', 'Adventure']
            )

class EventGuestForm(forms.ModelForm):
    class Meta:
        model = EventGuest
        fields = ['name', 'email', 'phone', 'is_primary_guest', 'plus_ones', 'dietary_restrictions']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Guest Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'is_primary_guest': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'plus_ones': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'dietary_restrictions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Dietary Restrictions'}),
        }

class EventTimelineForm(forms.ModelForm):
    class Meta:
        model = EventTimeline
        fields = ['title', 'description', 'start_time', 'end_time', 'responsible_person', 'is_critical']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Timeline Item Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'responsible_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Responsible Person'}),
            'is_critical': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class EventChecklistForm(forms.ModelForm):
    class Meta:
        model = EventChecklist
        fields = ['title', 'description', 'due_date', 'priority', 'assigned_to', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Checklist Item Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Assigned To'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category'}),
        }

class EventSearchForm(forms.Form):
    event_type = forms.ModelChoiceField(
        queryset=EventType.objects.filter(
            is_active=True,
            name__in=['Sports', 'Sports Tournament', 'Workshop', 'Cultural Festival', 'Music', 'Adventure']
        ),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    venue = forms.ModelChoiceField(
        queryset=Venue.objects.filter(status='active'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    min_guests = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min Guests'})
    )
    max_budget = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max Budget'})
    ) 

class EventReviewForm(forms.ModelForm):
    """Form for submitting event reviews with star ratings"""
    
    class Meta:
        model = EventReview
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.Select(
                choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)],
                attrs={'class': 'form-control rating-select'}
            ),
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Review Title (e.g., "Amazing Event Experience")',
                    'maxlength': '200'
                }
            ),
            'comment': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Share your experience and thoughts about this event...',
                    'maxlength': '1000'
                }
            ),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].label = 'Rating'
        self.fields['title'].label = 'Review Title'
        self.fields['comment'].label = 'Your Review'
    
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating and (rating < 1 or rating > 5):
            raise forms.ValidationError('Rating must be between 1 and 5 stars.')
        return rating
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title and len(title.strip()) < 5:
            raise forms.ValidationError('Review title must be at least 5 characters long.')
        return title.strip()
    
    def clean_comment(self):
        comment = self.cleaned_data.get('comment')
        if comment and len(comment.strip()) < 10:
            raise forms.ValidationError('Review comment must be at least 10 characters long.')
        return comment.strip() 