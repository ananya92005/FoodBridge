from django.urls import path

from .views import RouteEstimateView

urlpatterns = [path("estimate/", RouteEstimateView.as_view(), name="route-estimate")]

