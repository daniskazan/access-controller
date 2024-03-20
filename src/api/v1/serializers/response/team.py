from rest_framework import serializers

from core.models import User
from core.models.team import Team


class UserForTeamOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "full_name", "email"]


class TeamSerializer(serializers.ModelSerializer):
    team_lead = UserForTeamOutputSerializer()

    class Meta:
        model = Team
        fields = ["id", "name", "team_lead"]
