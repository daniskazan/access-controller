from django.contrib.auth.models import Permission
from rest_framework import serializers

from api.v1.serializers.response.team import TeamSerializer
from core.models import User


class UserAcceptInviteResponseSerializer(serializers.ModelSerializer):
    team = TeamSerializer()

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "team")


class UserRegistrationSerializerOutput(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ["password"]


class ConfirmApplicationByUserSerializer(serializers.ModelSerializer):
    position = serializers.ReadOnlyField(source="position.name")
    role = serializers.ReadOnlyField(source="role.name")

    class Meta:
        model = User
        fields = ["id", "full_name", "role", "position", "email"]


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = "__all__"


class UserFullOutputSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    position = serializers.ReadOnlyField(source="position.name")
    role = serializers.ReadOnlyField(source="role.name")
    full_name = serializers.CharField()
    team = TeamSerializer()

    class Meta:
        model = User
        exclude = [
            "password",
            "is_staff",
            "is_superuser",
            "username",
            "user_permissions",
            "groups",
        ]
