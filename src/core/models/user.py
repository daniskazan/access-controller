from django.db import models
from django.contrib.auth.models import AbstractUser

from core import mixins


class User(mixins.CreatedAtUpdatedAtMixin, AbstractUser):
    date_joined = None

    role = models.ForeignKey(
        "UserRole",
        on_delete=models.RESTRICT,
        blank=True,
        null=True,
        related_name="users",
        verbose_name="роль в системе",
    )
    email = models.EmailField(unique=True)
    team = models.ForeignKey("Team", on_delete=models.RESTRICT, blank=True, null=True)
    position = models.ForeignKey(
        "Position",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="users",
    )
    is_tenant_admin = models.BooleanField(default=False)

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
