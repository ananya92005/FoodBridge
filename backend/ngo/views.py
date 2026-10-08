from rest_framework import response, status, views

from food.serializers import FoodListingSerializer
from .serializers import NGOSerializer, NGOUpsertSerializer
from .services import get_or_create_profile, list_nearby_food, upsert_profile


class NGOProfileView(views.APIView):
    def get(self, request):
        profile = get_or_create_profile(request.user)
        return response.Response(NGOSerializer(profile).data)

    def put(self, request):
        profile = upsert_profile(request.user, request.data, NGOUpsertSerializer)
        return response.Response(NGOSerializer(profile).data, status=status.HTTP_200_OK)

    def patch(self, request):
        profile = upsert_profile(request.user, request.data, NGOUpsertSerializer)
        return response.Response(NGOSerializer(profile).data, status=status.HTTP_200_OK)


class NearbyFoodView(views.APIView):
    def get(self, request):
        listings = list_nearby_food(request.user, request.query_params.get("distance", 25))
        return response.Response(FoodListingSerializer(listings, many=True).data)

