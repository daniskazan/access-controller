from django.db import models
from django.utils.translation import gettext_lazy as _


class InvitationToken(models.Model):
    user = models.ForeignKey(
        "User", verbose_name=_("Пользователь"), on_delete=models.CASCADE
    )
    token = models.CharField(
        verbose_name=_("Токен приглашения"), max_length=255, db_index=True, unique=True
    )
    created_at = models.DateTimeField(
        verbose_name=_("Дата создания"), auto_now_add=True
    )
    expired_at = models.DateTimeField(verbose_name=_("Дата истечения"))

    class Meta:
        verbose_name = _("Токен приглашения")
        verbose_name_plural = _("Токены приглашения")

        unique_together = ("user", "token")
