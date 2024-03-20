from django.db import models
from django.utils.translation import gettext_lazy as _


class Position(models.Model):
    name = models.CharField(verbose_name=_("название должности"), max_length=255)

    class Meta:
        verbose_name = _("должность")
        verbose_name_plural = _("должности")

    def __str__(self):
        return f"{self.name}"
