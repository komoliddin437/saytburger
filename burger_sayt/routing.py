from apps.orders.routing import websocket_urlpatterns as order_ws_patterns

websocket_urlpatterns = [*order_ws_patterns]
