from core.models import User
from asgiref.sync import sync_to_async


@sync_to_async
def get_user_or_none(email: str):
    try:
        return User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return None


@sync_to_async
def save_user(user):
    user.save()
