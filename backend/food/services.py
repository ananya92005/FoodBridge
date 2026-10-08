from django.db.models import Q
from rest_framework.exceptions import PermissionDenied, ValidationError

from authentication.models import UserRole
from matching.services import auto_match_listing

from .models import FoodListing, FoodStatus


def create_listing(user, payload, serializer_class):
    if user.role != UserRole.DONOR:
        raise PermissionDenied("Only donors can create food listings.")
    serializer = serializer_class(data=payload)
    serializer.is_valid(raise_exception=True)
    listing = serializer.save(donor=user)
    auto_match_listing(listing)
    return listing


def update_listing(instance, payload, serializer_class):
    serializer = serializer_class(instance, data=payload, partial=True)
    serializer.is_valid(raise_exception=True)
    listing = serializer.save()
    auto_match_listing(listing)
    return listing


def donor_listings(user):
    return FoodListing.objects.filter(donor=user).select_related("donor").prefetch_related("assignments__ngo__user")


def available_listings():
    return FoodListing.objects.filter(
        Q(status=FoodStatus.OPEN) | Q(status=FoodStatus.MATCHED)
    ).select_related("donor").prefetch_related("assignments__ngo__user")
