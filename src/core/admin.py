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
from core.forms.admin_user import SendMessageForm

from core.models import User
from core.models import Position
from core.models import UserRole
from core.models import Resource, ResourceGroup
from core.models import Team
from core.models import Application
from core.models import Grant
from core.models import InvitationToken
from producer import producer, EventType


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
    actions = ("send_message",)
    list_display = (
        "id",
        "status",
        "user",
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


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    actions = ()
    list_display = ("id", "name")
    list_filter = ("name",)


admin.site.register(UserRole)
admin.site.register(Resource)
admin.site.register(ResourceGroup)
admin.site.register(Team)
