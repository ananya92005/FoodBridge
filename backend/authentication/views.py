from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import FoodBridgeTokenSerializer
from .services import get_user_payload, register_user


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        return Response(register_user(request.data), status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    serializer_class = FoodBridgeTokenSerializer


class MeView(APIView):
    def get(self, request):
        return Response(get_user_payload(request.user))

