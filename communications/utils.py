from users.models import CustomUser

def get_allowed_chat_targets(user):
    """
    Returns a queryset of users the given user is allowed to chat with, based on their role.
    """
    if user.is_superuser:
        return CustomUser.objects.exclude(id=user.id)
    if hasattr(user, 'is_administrator') and user.is_administrator:
        return CustomUser.objects.exclude(id=user.id)
    if hasattr(user, 'is_event_manager') and user.is_event_manager:
        return CustomUser.objects.filter(user_type__in=['user', 'admin']).exclude(id=user.id)
    if hasattr(user, 'is_regular_user') and user.is_regular_user:
        return CustomUser.objects.filter(user_type='manager').exclude(id=user.id)
    return CustomUser.objects.none() 