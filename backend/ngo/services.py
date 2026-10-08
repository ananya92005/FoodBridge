from rest_framework.exceptions import PermissionDenied

from authentication.models import UserRole
from food.models import FoodListing, FoodStatus
from routing.services import haversine_distance_km

from .models import NGO


def get_or_create_profile(user):
    if user.role != UserRole.NGO:
        raise PermissionDenied("Only NGO users can manage NGO profiles.")
    profile, _ = NGO.objects.get_or_create(
        user=user,
        defaults={
            "name": "",
            "city": "",
            "district": "",
            "capacity": 0,
            "latitude": 0,
            "longitude": 0,
        },
    )
    return profile


def upsert_profile(user, payload, serializer_class):
    profile = get_or_create_profile(user)
    serializer = serializer_class(profile, data=payload, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer.instance


def list_nearby_food(user, max_distance_km=25):
    profile = get_or_create_profile(user)
    listings = FoodListing.objects.filter(status__in=[FoodStatus.OPEN, FoodStatus.MATCHED]).select_related("donor")
    results = []
    for listing in listings:
        distance = haversine_distance_km(profile.latitude, profile.longitude, listing.latitude, listing.longitude)
        if distance <= float(max_distance_km):
            listing.distance_km = round(distance, 2)
            results.append(listing)
    return sorted(results, key=lambda item: item.distance_km)
