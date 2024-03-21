from django.db import models

from core.mixins import CreatedAtUpdatedAtMixin
from core.enums.grant import GrantStatus


class Grant(CreatedAtUpdatedAtMixin, models.Model):
    user = models.ForeignKey("User", null=False, related_name="grants", on_delete=models.DO_NOTHING)
    resource = models.ForeignKey("Resource", null=False, on_delete=models.DO_NOTHING)
    status = models.CharField(choices=GrantStatus.choices, default=GrantStatus.PENDING, max_length=128)

    class Meta:
        verbose_name = "право доступа"
        verbose_name_plural = "права доступа"

    def __str__(self):
        return f"Grant - {self.user.full_name} - {self.resource.name}"
