from datetime import datetime

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from api.v1.serializers.response.team import TeamSerializer
from api.v1.serializers.response.user import UserAcceptInviteResponseSerializer
from core.models import User, InvitationToken
from core.enums.user import UserInvitationStatusChoice


class GetTokenStatusSerializer(serializers.Serializer):
    invite_token = serializers.CharField(required=True)

    def validate(self, attrs: dict) -> dict:
        get_object_or_404(
            InvitationToken,
            token=attrs["invite_token"],
            expired_at__gt=datetime.utcnow(),
        )
        return attrs

    def create(self, validated_data: dict) -> User:
        invitation_token = InvitationToken.objects.get(
            token=validated_data["invite_token"], expired_at__gt=datetime.utcnow()
        )
        user = invitation_token.user

        if user.invite_status == UserInvitationStatusChoice.SUCCESS:
            raise ValidationError(
                {"invite_token": "Пользователь уже принял приглашение"}
            )

        return user

    def to_representation(self, instance: User):
        return UserAcceptInviteResponseSerializer(instance=instance).data


class UserInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "team", "role"]

    def create(self, validated_data: dict):
        validated_data.update({"username": validated_data["email"]})
        user = super().create(validated_data)
        return user


class UserAcceptInviteSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    password = serializers.CharField()

    class Meta:
        model = User
        fields = ("id", "password")

    def update(self, instance: User, validated_data: dict):
        instance = super().update(instance, validated_data)
        instance.is_active = True
        instance.invite_status = UserInvitationStatusChoice.SUCCESS
        instance.set_password(validated_data["password"])
        instance.save()
        return instance

    def to_representation(self, instance: User):
        return UserAcceptInviteResponseSerializer(instance=instance).data
