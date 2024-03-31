from django.db import models

from core.mixins import CreatedAtUpdatedAtMixin


class CommandPattern(CreatedAtUpdatedAtMixin, models.Model):
    command_name = models.CharField(
        help_text="Название команды", default="undefined", null=False, blank=False
    )
    resource = models.ForeignKey(
        "Resource", on_delete=models.CASCADE, related_name="executing_commands"
    )
    executing_pattern = models.TextField(null=False, blank=False)

    class Meta:
        verbose_name = "Шаблон скрипта"
        verbose_name_plural = "Шаблоны скриптов"

    def __str__(self):
        return self.command_name
