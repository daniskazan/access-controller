from dataclasses import asdict
from django.contrib import admin
from django.contrib import messages
from django.http import HttpRequest
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.contrib.auth.models import Permission
from django.db.models import QuerySet
from django.http import HttpResponseRedirect
from django.shortcuts import render

from api.v1.views.application import GrantActivatedEvent
from bot.logic.notifier import TelegramBotNotifier
from core.forms.admin_user import SendMessageForm
from core.forms.admin_grant import ActivateGrantForm

from core.models import User
from core.models import Position
from core.models import UserRole
from core.models import Resource, ResourceGroup
from core.models import Team
from core.models import Application
from core.models import Grant
from core.models import InvitationToken
from core.models import CommandPattern
from core.services.grant import DatabaseCommandExecutor
from core.services.mailing import EmailService
from producer import producer, EventType
from utils.security.hasher import Hashing


@admin.register(CommandPattern)
class CommandAdmin(admin.ModelAdmin):
    list_display = ("id", "command_name", "resource", "executing_pattern")


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "codename")


@admin.register(InvitationToken)
class InvitationTokenAdmin(admin.ModelAdmin):
    list_filter = ("user__email",)
    list_display = ("id", "token", "expired_at", "user")


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_filter = ("email", "is_active")
    readonly_fields = ("id", "created_at", "updated_at", "password")
    list_display = (
        "id",
        "first_name",
        "last_name",
    )

    search_fields = ["first_name", "last_name", "email"]


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    actions = ()
    search_fields = ("user__first_name", "resource__name")
    list_display = (
        "id",
        "status",
        "user",
        "resource",
    )
    list_filter = ("status",)


@admin.register(Grant)
class GrantAdmin(admin.ModelAdmin):
    actions = ("send_message", "activate_db_grant")
    list_display = (
        "id",
        "status",
        "user",
        "scope",
        "resource",
    )
    list_filter = ("status", "resource__resource_group")

    def send_message(self, request: HttpRequest, queryset: QuerySet[Grant]):
        form = None
        if "apply" in request.POST:
            form = SendMessageForm(request.POST)
            if form.is_valid():
                message = form.cleaned_data["message"]
                if len(queryset) > 1:
                    self.message_user(
                        request, "Надо выбрать только одного получателя", messages.ERROR
                    )
                    return HttpResponseRedirect(request.get_full_path())

                grant: Grant = queryset.first()
                subject = f"Access for {grant.resource.name} is active."
                EmailService.send_email(
                    subject=subject,
                    message=message,
                    recipients_email=[grant.user.email],
                )
                TelegramBotNotifier(tenant=request.tenant).notify(
                    user=grant.user, message=f"{subject}. Check your email."
                )
                producer.publish(
                    routing_key=EventType.GRANT_ACTIVATED,
                    message=asdict(
                        GrantActivatedEvent(
                            application_id=grant.application.pk,
                        )
                    ),
                )
                self.message_user(
                    request,
                    f'Сообщение "{message}" отправлено ',
                )
                return HttpResponseRedirect(request.get_full_path())
        if not form:
            form = SendMessageForm(
                initial={"_selected_action": request.POST.getlist(ACTION_CHECKBOX_NAME)}
            )
        return render(
            request,
            "mailing/send_message.html",
            {"users": queryset, "form": form, "title": "Отправить сообщение"},
        )

    send_message.short_description = "Отправить сообщение"

    def activate_db_grant(self, request: HttpRequest, queryset: QuerySet[Grant]):
        grant = queryset.first()
        if "apply" in request.POST:
            form = ActivateGrantForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                db = DatabaseCommandExecutor(
                    db_url=cd["db_url"], running_script=cd["command"], grant=grant
                )
                try:
                    db.execute()
                    # Теперь все в порядке, перенаправляем пользователя на ту же страницу
                    self.message_user(request, "Успешно", messages.SUCCESS)
                    return HttpResponseRedirect(request.get_full_path())
                except Exception as e:
                    self.message_user(
                        request, f"Произошла ошибка: {e.args}", messages.ERROR
                    )

        # Если запрос не POST или форма не валидна, вернем пустую форму
        form = ActivateGrantForm(
            initial={"_selected_action": request.POST.getlist(ACTION_CHECKBOX_NAME)}
        )
        # Возвращаем шаблон с формой
        return render(
            request,
            "mailing/activate_grant.html",
            {"users": queryset, "form": form, "title": "Выдать доступ"},
        )

    activate_db_grant.short_description = "Выдать доступ к базе данных"


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    actions = ()
    list_display = ("id", "name")
    list_filter = ("name",)


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "resource_group", "get_resource_url")
    readonly_fields = ("created_at", "updated_at")

    def get_resource_url(self, obj: Resource):
        if obj.resource_url:
            return Hashing.decrypt(obj.resource_url)
        return None

    get_resource_url.short_description = "Resource url"

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ("resource_url",)
        return self.readonly_fields


admin.site.register(UserRole)
admin.site.register(ResourceGroup)
admin.site.register(Team)
