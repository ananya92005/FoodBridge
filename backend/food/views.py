from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from authentication.models import UserRole
from .serializers import FoodListingSerializer, FoodListingWriteSerializer
from .services import available_listings, create_listing, donor_listings, update_listing


class FoodListingViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == UserRole.DONOR:
            return donor_listings(self.request.user)
        return available_listings()

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return FoodListingWriteSerializer
        return FoodListingSerializer

    def create(self, request, *args, **kwargs):
        listing = create_listing(request.user, request.data, FoodListingWriteSerializer)
        return Response(
            FoodListingSerializer(listing, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        self.require_listing_manager(request.user)
        listing = update_listing(self.get_object(), request.data, FoodListingWriteSerializer)
        return Response(FoodListingSerializer(listing, context=self.get_serializer_context()).data)

    def partial_update(self, request, *args, **kwargs):
        self.require_listing_manager(request.user)
        listing = update_listing(self.get_object(), request.data, FoodListingWriteSerializer)
        return Response(FoodListingSerializer(listing, context=self.get_serializer_context()).data)

    def destroy(self, request, *args, **kwargs):
        self.require_listing_manager(request.user)
        return super().destroy(request, *args, **kwargs)

    @staticmethod
    def require_listing_manager(user):
        if user.role not in (UserRole.DONOR, UserRole.ADMIN):
            raise PermissionDenied("Only donors or admins can change food listings.")
