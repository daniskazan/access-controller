from django.db import models

from core.mixins import CreatedAtUpdatedAtMixin
from core.enums.grant import GrantStatus
from core.enums.application import ApplicationScopeChoice


class Grant(CreatedAtUpdatedAtMixin, models.Model):
    user = models.ForeignKey(
        "User", null=False, related_name="grants", on_delete=models.DO_NOTHING
    )
    resource = models.ForeignKey("Resource", null=False, on_delete=models.DO_NOTHING)
    status = models.CharField(
        choices=GrantStatus.choices, default=GrantStatus.PENDING, max_length=128
    )
    application = models.OneToOneField(
        to="Application", on_delete=models.SET_NULL, null=True
    )
    scope = models.IntegerField(
        choices=ApplicationScopeChoice.choices,
        null=False,
        default=ApplicationScopeChoice.READ_SCOPE,
    )

    class Meta:
        verbose_name = "право доступа"
        verbose_name_plural = "права доступа"

    def __str__(self):
        return f"Grant - {self.user.full_name} - {self.resource.name}"
