import math

from django.utils import timezone


EARTH_RADIUS_KM = 6371.0


def haversine_distance_km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def estimate_route(origin, destination):
    distance_km = haversine_distance_km(
        origin["latitude"],
        origin["longitude"],
        destination["latitude"],
        destination["longitude"],
    )
    estimated_minutes = max(5, round((distance_km / 30) * 60))
    return {
        "distance_km": round(distance_km, 2),
        "estimated_minutes": estimated_minutes,
        "generated_at": timezone.now(),
    }

