from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from assignments.models import Assignment
from food.models import FoodStatus
from ngo.models import NGO
from notifications.services import create_notification
from routing.services import haversine_distance_km


def _expiry_urgency_score(expiry_time):
    remaining = max((expiry_time - timezone.now()).total_seconds(), 1)
    capped = min(remaining, timedelta(hours=24).total_seconds())
    return 1 - (capped / timedelta(hours=24).total_seconds())


def _capacity_fit_score(capacity, quantity):
    if capacity <= 0:
        return 0
    return min(quantity / capacity, 1)


def score_ngo(listing, ngo):
    distance_km = haversine_distance_km(listing.latitude, listing.longitude, ngo.latitude, ngo.longitude)
    distance_threshold = float(settings.MATCH_DISTANCE_THRESHOLD_KM)
    if distance_km > distance_threshold or ngo.capacity < listing.quantity:
        return None

    normalized_distance = distance_km / max(distance_threshold, 1)
    urgency = _expiry_urgency_score(listing.expiry_time)
    capacity_fit = _capacity_fit_score(ngo.capacity, listing.quantity)

    score = (0.5 * (1 - normalized_distance)) + (0.3 * urgency) + (0.2 * capacity_fit)
    return {
        "ngo": ngo,
        "distance_km": round(distance_km, 2),
        "score": round(score, 4),
    }


def rank_ngos_for_listing(listing):
    ngo_profiles = NGO.objects.filter(is_active=True).select_related("user")
    ranked = []
    for ngo in ngo_profiles:
        candidate = score_ngo(listing, ngo)
        if candidate:
            ranked.append(candidate)
    return sorted(ranked, key=lambda item: item["score"], reverse=True)


def auto_match_listing(listing):
    ranked = rank_ngos_for_listing(listing)
    if not ranked:
        listing.status = FoodStatus.OPEN
        listing.save(update_fields=["status", "updated_at"])
        return None

    best = ranked[0]
    assignment, _ = Assignment.objects.update_or_create(
        food=listing,
        ngo=best["ngo"],
        defaults={"match_score": best["score"]},
    )
    listing.status = FoodStatus.MATCHED
    listing.save(update_fields=["status", "updated_at"])

    create_notification(
        best["ngo"].user,
        "New matched food listing",
        f"A {listing.food_type} donation has been matched to your NGO.",
    )
    return {
        "assignment_id": assignment.id,
        "ngo_id": best["ngo"].id,
        "distance_km": best["distance_km"],
        "score": best["score"],
    }

