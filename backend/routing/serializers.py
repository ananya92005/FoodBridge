from rest_framework import serializers


class RoutePointSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()


class RouteEstimateSerializer(serializers.Serializer):
    origin = RoutePointSerializer()
    destination = RoutePointSerializer()

