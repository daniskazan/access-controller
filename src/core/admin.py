from django.contrib import admin
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.contrib.auth.models import Permission
from django.http import HttpResponseRedirect
from django.shortcuts import render

from core.forms.admin_user import SendMessageForm
from core.models import User
from core.models import Position
from core.models import UserRole
from core.models import Resource, ResourceGroup
from core.models import Team
from core.models import Application
from core.models import Grant


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_filter = (
        "email",
        "is_active"
    )
    list_display = (
        "id",
        "first_name",
        "last_name"
    )
    search_fields = ["first_name", "last_name", "email"]


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    actions = (

    )
    search_fields = (
        "user__first_name",
        "resource__name"
    )
    list_display = (
        "id",
        "status",
        "user",
        "resource",
    )
    list_filter = (
        "status",
    )


@admin.register(Grant)
class GrantAdmin(admin.ModelAdmin):
    actions = (

    )
    list_display = (
        "id",
        "status",
        "user",
        "resource",
    )
    list_filter = (
        "status",
    )


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    actions = (

    )
    list_display = (
        "id",
        "name"
    )
    list_filter = (
        "name",
    )


admin.site.register(UserRole)
admin.site.register(Resource)
admin.site.register(ResourceGroup)
admin.site.register(Team)
