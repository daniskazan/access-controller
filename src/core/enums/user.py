from django.db import models


class UserInvitationStatusChoice(models.TextChoices):
    PENDING = "pending", "Pending"
    SUCCESS = "success", "Success"
