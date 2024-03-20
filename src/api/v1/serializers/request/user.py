from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from core.models import User


class UserInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "team", "role"]


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
