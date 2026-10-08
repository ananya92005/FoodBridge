from django.urls import path
from django.http import JsonResponse
from rest_framework_simplejwt.views import TokenRefreshView

from .views import LoginView, MeView, RegisterView


def auth_root(request):
    return JsonResponse(
        {
            "service": "FoodBridge authentication API",
            "endpoints": {
                "POST /api/auth/register/": "Create an account",
                "POST /api/auth/login/": "Get access and refresh tokens",
                "POST /api/auth/refresh/": "Refresh an access token",
                "GET /api/auth/me/": "Get the signed-in user",
            },
        }
    )


urlpatterns = [
    path("", auth_root, name="auth-root"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", MeView.as_view(), name="me"),
]
