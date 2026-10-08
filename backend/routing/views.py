from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RouteEstimateSerializer
from .services import estimate_route


class RouteEstimateView(APIView):
    def post(self, request):
        serializer = RouteEstimateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        return Response(estimate_route(data["origin"], data["destination"]))

