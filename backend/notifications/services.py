from .models import Notification
from .tasks import broadcast_notification


def create_notification(user, title, message):
    notification = Notification.objects.create(user=user, title=title, message=message)
    payload = {
        "id": notification.id,
        "user_id": user.id,
        "title": title,
        "message": message,
        "is_read": notification.is_read,
        "created_at": notification.created_at.isoformat(),
    }
    broadcast_notification.delay(payload)
    return notification

