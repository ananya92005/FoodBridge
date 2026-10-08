from rest_framework.routers import DefaultRouter

from .views import FoodListingViewSet

router = DefaultRouter()
router.register("listings", FoodListingViewSet, basename="food-listing")

urlpatterns = router.urls

