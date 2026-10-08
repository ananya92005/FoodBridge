from django.shortcuts import get_object_or_404
from rest_framework import response, views

from food.models import FoodListing
from .serializers import MatchPreviewSerializer
from .services import rank_ngos_for_listing


class MatchPreviewView(views.APIView):
    def post(self, request):
        serializer = MatchPreviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        listing = get_object_or_404(FoodListing, id=serializer.validated_data["listing_id"])
        ranked = rank_ngos_for_listing(listing)
        return response.Response(
            [
                {
                    "ngo_id": item["ngo"].id,
                    "ngo_name": item["ngo"].name,
                    "score": item["score"],
                    "distance_km": item["distance_km"],
                }
                for item in ranked
            ]
        )

