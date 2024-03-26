from django.db import models
from django.utils.translation import gettext_lazy as _

from core.enums.application import ApplicationStatusChoice, ApplicationScopeChoice
from core.mixins import CreatedAtUpdatedAtMixin


class Application(CreatedAtUpdatedAtMixin, models.Model):
    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="applications"
    )
    confirm_by = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="applications_to_confirm"
    )
    resource = models.ForeignKey(
        "Resource", on_delete=models.SET_NULL, null=True, blank=True
    )
    status = models.IntegerField(
        choices=ApplicationStatusChoice, default=ApplicationStatusChoice.IN_PROCESS
    )
    scope = models.IntegerField(
        choices=ApplicationScopeChoice, default=ApplicationScopeChoice.READ_SCOPE
    )

    class Meta:
        verbose_name = _("заявка")
        verbose_name_plural = _("заявки")
        permissions = (("can_approve_application", "Can_approve_application"),)

    def __str__(self):
        return f"Application #{self.pk}, User #{self.user_id}, Scopes - {self.get_scope_display()}"
