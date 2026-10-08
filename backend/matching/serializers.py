from rest_framework import serializers


class MatchPreviewSerializer(serializers.Serializer):
    listing_id = serializers.IntegerField()

