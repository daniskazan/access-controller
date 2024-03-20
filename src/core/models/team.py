from django.db import models
from django.utils.translation import gettext_lazy as _


class Team(models.Model):
    name = models.CharField(verbose_name=_("название команды"), max_length=255)
    team_lead = models.OneToOneField(
        "User",
        verbose_name=_("тимлид"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="team_leads",
    )
    team = models.ManyToManyField(
        "User", verbose_name=_("разработчики"), blank=True, related_name="user_team"
    )

    class Meta:
        verbose_name = _("команда")
        verbose_name_plural = _("команды")

    def __str__(self):
        return f"{self.name}"
