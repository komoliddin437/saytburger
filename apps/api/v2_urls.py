from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import my_orders
from .v2_views import BranchViewSet, OrderViewSet, PaymentWebhookView, ProductV2ViewSet

router = DefaultRouter()
router.register("branches", BranchViewSet, basename="v2-branch")
router.register("products", ProductV2ViewSet, basename="v2-product")
router.register("orders", OrderViewSet, basename="v2-order")

urlpatterns = [
    path("", include(router.urls)),
    path("orders/me/", my_orders, name="v2-my-orders"),
    path("payments/webhook/<str:provider>/", PaymentWebhookView.as_view(), name="v2-payment-webhook"),
]
