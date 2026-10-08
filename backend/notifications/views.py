from django.shortcuts import get_object_or_404
from rest_framework import response, views

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(views.APIView):
    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)
        return response.Response(NotificationSerializer(notifications, many=True).data)


class NotificationReadView(views.APIView):
    def post(self, request, notification_id):
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.is_read = True
        notification.save(update_fields=["is_read"])
        return response.Response(NotificationSerializer(notification).data)

