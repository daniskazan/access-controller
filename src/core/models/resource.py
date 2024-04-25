from django.db import models

from core.mixins import CreatedAtUpdatedAtMixin
from utils.security.hasher import Hashing


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
    resource_url = models.CharField(null=True, blank=True)
    name = models.CharField(max_length=256)
    commands = models.ManyToManyField(
        "CommandPattern", null=True, blank=True, related_name="resource_commands"
    )

    def __str__(self):
        return f"{self.__class__.__name__} - {self.name}"

    class Meta:
        verbose_name = "ресурс"
        verbose_name_plural = "ресурсы"

    def full_clean(self, exclude=None, validate_unique=True, validate_constraints=True):
        if self.resource_url:
            x = Hashing.encrypt(self.resource_url)
            self.resource_url = Hashing.encrypt(self.resource_url)
        return super().full_clean(
            exclude=exclude,
            validate_unique=validate_unique,
            validate_constraints=validate_constraints,
        )
