from datetime import datetime

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from core.models import User, InvitationToken
from core.enums.user import UserInvitationStatusChoice


class UserAcceptInviteSerializer(serializers.Serializer):

    invite_token = serializers.CharField(required=True)

    def validate(self, attrs: dict) -> dict:
        get_object_or_404(InvitationToken, token=attrs["invite_token"], expired_at__gt=datetime.utcnow())
        return attrs

    def create(self, validated_data: dict) -> User:
        invitation_token = InvitationToken.objects.get(
            token=validated_data["invite_token"], expired_at__gt=datetime.utcnow()
        )
        user = invitation_token.user

        if user.invite_status == UserInvitationStatusChoice.SUCCESS:
            raise ValidationError({"invite_token": "Пользователь уже принял приглашение"})

        return user

    def to_representation(self, instance: User):
        return UserFullOutputSerializer(instance=instance).data


class UserInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "team", "role"]

    def create(self, validated_data: dict):
        user = super().create(validated_data)
        user.username = validated_data["email"]
        return user


class UserFullOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password", "team", "role"]

    def create(self, validated_data: dict) -> User:
        username: str = validated_data["email"]
        validated_data.update({"username": username})
        user = User(**validated_data)
        user.set_password(raw_password=validated_data["password"])
        user.save()
        return user
