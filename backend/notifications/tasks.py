from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer


@shared_task
def broadcast_notification(payload):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{payload['user_id']}",
        {"type": "notify.message", "payload": payload},
    )

