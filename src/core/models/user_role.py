from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.enums.user_role import UserRoleDefaultChoice


class UserRole(models.Model):
    name = models.CharField(
        default=UserRoleDefaultChoice.EMPLOYEE,
        verbose_name=_("роль в системе"),
        max_length=255,
        blank=True,
        null=True,
        unique=True,
    )
    groups = models.ManyToManyField(
        Group,
        verbose_name=_("группы"),
        blank=True,
        help_text=_(
            "Группы, к которым принадлежит этот пользователь. "
            "Пользователь получит все разрешения, предоставленные каждой из его групп."
        ),
        related_name="roles",
    )

    def __str__(self):
        return f"UserRole - {self.name}"

    class Meta:
        verbose_name = _("роль в системе")
        verbose_name_plural = _("роли в системе")
