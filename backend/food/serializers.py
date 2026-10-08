from rest_framework import serializers

from authentication.serializers import UserSerializer
from .models import FoodListing


class FoodListingWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodListing
        fields = (
            "id",
            "food_type",
            "quantity",
            "description",
            "expiry_time",
            "latitude",
            "longitude",
            "status",
        )
        read_only_fields = ("id", "status")


class FoodListingSerializer(serializers.ModelSerializer):
    donor = UserSerializer(read_only=True)
    assignment = serializers.SerializerMethodField()
    distance_km = serializers.FloatField(read_only=True)

    class Meta:
        model = FoodListing
        fields = (
            "id",
            "donor",
            "food_type",
            "quantity",
            "description",
            "expiry_time",
            "latitude",
            "longitude",
            "status",
            "distance_km",
            "assignment",
            "created_at",
            "updated_at",
        )

    def get_assignment(self, obj):
        assignment = obj.assignments.select_related("ngo__user").order_by("-created_at").first()
        if not assignment:
            return None
        return {
            "id": assignment.id,
            "status": assignment.status,
            "ngo": {
                "id": assignment.ngo.id,
                "name": assignment.ngo.name,
                "user": {
                    "id": assignment.ngo.user.id,
                    "email": assignment.ngo.user.email,
                },
            },
        }

