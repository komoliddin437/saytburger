from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def push_order_status(order):
    try:
        channel_layer = get_channel_layer()
        if channel_layer is None:
            return
        payload = {
            "order_id": order.id,
            "status": order.status,
            "payment_status": order.payment_status,
            "updated_at": order.updated_at.isoformat(),
        }
        async_to_sync(channel_layer.group_send)(
            f"order_{order.id}",
            {"type": "order_status_update", "payload": payload},
        )
    except Exception:
        # Order creation should never fail because websocket push is unavailable.
        return
