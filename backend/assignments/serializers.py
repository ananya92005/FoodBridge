from rest_framework import serializers

from food.serializers import FoodListingSerializer
from ngo.serializers import NGOSerializer
from .models import Assignment


class AssignmentSerializer(serializers.ModelSerializer):
    food = FoodListingSerializer(read_only=True)
    ngo = NGOSerializer(read_only=True)

    class Meta:
        model = Assignment
        fields = (
            "id",
            "food",
            "ngo",
            "status",
            "match_score",
            "notes",
            "created_at",
            "updated_at",
        )

