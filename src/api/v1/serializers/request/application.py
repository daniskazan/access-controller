from rest_framework import serializers

from api.v1.serializers.response.user import ConfirmApplicationByUserSerializer
from core.models import User, Application


class CreateApplicationSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Application
        fields = ["user", "resource"]

    def fetch_team_lead(self) -> User:
        user = self.context["request"].user
        return user.team.team_lead

    def create(self, validated_data: dict) -> Application:
        validated_data.update({"confirm_by": self.fetch_team_lead()})
        return super(CreateApplicationSerializer, self).create(validated_data)


class FullApplicationSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.full_name")
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    resource = serializers.ReadOnlyField(source="resource.name")
    status = serializers.CharField(source="get_status_display")
    confirm_by = ConfirmApplicationByUserSerializer()

    class Meta:
        model = Application
        fields = "__all__"
        # exclude = ["user"]
