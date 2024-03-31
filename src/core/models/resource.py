from django.db import models

from core.mixins import CreatedAtUpdatedAtMixin


class ResourceGroup(CreatedAtUpdatedAtMixin, models.Model):
    name = models.CharField(null=False, blank=False, max_length=256)

    class Meta:
        verbose_name = "группа ресурсов"
        verbose_name_plural = "группы ресурсов"

    def __str__(self):
        return f"{self.__class__.__name__} - {self.name}"


class Resource(CreatedAtUpdatedAtMixin, models.Model):
    resource_group = models.ForeignKey(
        "ResourceGroup", on_delete=models.CASCADE, related_name="resources"
    )
    name = models.CharField(max_length=256)
    url = models.CharField(
        help_text="URL ресурса(необходим если хотите выполнять команды, например отправлять запросы в БД)",
        null=True,
    )
    commands = models.ManyToManyField(
        "CommandPattern", related_name="resource_commands"
    )

    def __str__(self):
        return f"{self.__class__.__name__} - {self.name}"

    class Meta:
        verbose_name = "ресурс"
        verbose_name_plural = "ресурсы"
