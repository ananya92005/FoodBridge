from rest_framework import serializers

from authentication.serializers import UserSerializer
from .models import NGO


class NGOSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = NGO
        fields = (
            "id",
            "user",
            "name",
            "city",
            "district",
            "capacity",
            "latitude",
            "longitude",
            "is_active",
            "created_at",
            "updated_at",
        )


class NGOUpsertSerializer(serializers.ModelSerializer):
    class Meta:
        model = NGO
        fields = ("name", "city", "district", "capacity", "latitude", "longitude", "is_active")
