from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def api_root(request):
    return JsonResponse(
        {
            "service": "FoodBridge API",
            "endpoints": {
                "GET /api/auth/": "List authentication endpoints",
                "POST /api/auth/register/": "Create an account",
                "POST /api/auth/login/": "Get access and refresh tokens",
                "POST /api/auth/refresh/": "Refresh an access token",
                "GET /api/auth/me/": "Get the signed-in user",
                "GET /api/users/": "List users",
                "GET, POST /api/food/listings/": "List or create food listings",
                "GET, PUT, PATCH, DELETE /api/food/listings/<id>/": "Read or change a food listing",
                "GET, PUT, PATCH /api/ngo/profile/": "Read or update an NGO profile",
                "GET /api/ngo/nearby-food/": "Find nearby food listings",
                "POST /api/matching/preview/": "Preview NGO matches for a listing",
                "POST /api/routing/estimate/": "Estimate distance and travel time",
                "GET /api/notifications/": "List notifications",
                "POST /api/notifications/<id>/read/": "Mark a notification as read",
                "GET /api/assignments/": "List assignments",
                "POST /api/assignments/<id>/<accept|reject|complete>/": "Change assignment status",
                "GET /admin/": "Django admin",
            },
        }
    )


urlpatterns = [
    path("", api_root, name="api-root"),
    path("api/", api_root, name="api-index"),
    path("admin/", admin.site.urls),
    path("api/auth/", include("authentication.urls")),
    path("api/users/", include("users.urls")),
    path("api/food/", include("food.urls")),
    path("api/ngo/", include("ngo.urls")),
    path("api/matching/", include("matching.urls")),
    path("api/routing/", include("routing.urls")),
    path("api/notifications/", include("notifications.urls")),
    path("api/assignments/", include("assignments.urls")),
]
