from django.db import models


class UserRoleDefaultChoice(models.TextChoices):
    ADMINISTRATOR = "admin", "Administrator"
    EMPLOYEE = "employee", "Employee"
