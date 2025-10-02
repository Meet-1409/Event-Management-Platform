from django import forms
from users.models import CustomUser
from .models import ChatRoom, ChatRoomMember

class GroupChatCreateForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Select Members"
    )

    class Meta:
        model = ChatRoom
        fields = ['name', 'description', 'chat_type', 'users']

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('current_user')
        super().__init__(*args, **kwargs)
        # Only allow users that the current user can add (role-based)
        allowed_roles = ['user', 'manager', 'admin']
        if current_user.is_superuser:
            self.fields['users'].queryset = CustomUser.objects.exclude(id=current_user.id)
        elif current_user.user_type == 'admin':
            self.fields['users'].queryset = CustomUser.objects.filter(user_type__in=['manager', 'user']).exclude(id=current_user.id)
        elif current_user.user_type == 'manager':
            self.fields['users'].queryset = CustomUser.objects.filter(user_type='user').exclude(id=current_user.id)
        else:
            self.fields['users'].queryset = CustomUser.objects.none() 