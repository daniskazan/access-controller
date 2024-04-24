from django.db import models
from django.utils.translation import gettext_lazy as _
from django_tenants.models import DomainMixin, TenantMixin

from core.mixins import CreatedAtUpdatedAtMixin


class TenantCreationRequest(CreatedAtUpdatedAtMixin):
    modified = None

    tenant_name = models.CharField(
        max_length=100, verbose_name=_("имя тенанта"), unique=True
    )
    domain = models.CharField(max_length=253, verbose_name=_("домен"), unique=True)
    admin_email = models.EmailField(verbose_name=_("email админа"))

    class Meta:
        verbose_name = _("Запрос на создание тенанта")
        verbose_name_plural = _("Запросы на создание тенанта")


class Tenant(TenantMixin, CreatedAtUpdatedAtMixin):
    name = models.CharField(max_length=100)
    admin_email = models.EmailField(
        verbose_name=_("Email админа тенанта"), default=None, null=True, blank=True
    )
    telegram_bot_token = models.CharField(
        max_length=46,
        help_text="Read more: https://core.telegram.org/bots#3-how-do-i-create-a-bot",
        null=True,
        blank=True,
    )

    # default true, schema will be automatically created and synced when it is saved
    auto_create_schema = True

    class Meta:
        verbose_name = "Заказчик"
        verbose_name_plural = "Заказчики"


class Domain(DomainMixin):
    class Meta:
        verbose_name = "Адрес заказчика"
        verbose_name_plural = "Адреса заказчиков"
