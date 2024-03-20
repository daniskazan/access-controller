from django.db import models


class GrantStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    ACTIVE = "active", "Active"
    WAITING_REVOCATION = "revocation", "Revocation"
