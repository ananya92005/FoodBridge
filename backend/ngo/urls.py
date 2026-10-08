from django.urls import path

from .views import NearbyFoodView, NGOProfileView

urlpatterns = [
    path("profile/", NGOProfileView.as_view(), name="ngo-profile"),
    path("nearby-food/", NearbyFoodView.as_view(), name="ngo-nearby-food"),
]

