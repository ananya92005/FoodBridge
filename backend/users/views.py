from rest_framework import generics

from .serializers import PublicUserSerializer
from .services import list_users


class UserListView(generics.ListAPIView):
    serializer_class = PublicUserSerializer

    def get_queryset(self):
        return list_users(self.request.query_params.get("role"))

