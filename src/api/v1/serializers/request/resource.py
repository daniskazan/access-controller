from rest_framework import serializers
from core.models import Resource


class ResourceSerializer(serializers.ModelSerializer):
    resource_group = serializers.CharField(source="resource_group.name")

    class Meta:
        model = Resource
        fields = "__all__"
