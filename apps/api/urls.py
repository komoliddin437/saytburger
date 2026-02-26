from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BranchViewSet,
    CategoryViewSet,
    OrderViewSet,
    PaymentWebhookView,
    ProductViewSet,
    ProfileView,
    ReservationViewSet,
    WishlistViewSet,
    GuestCheckoutView,
    my_orders,
)

router = DefaultRouter()
router.register("branches", BranchViewSet, basename="branch")
router.register("categories", CategoryViewSet, basename="category")
router.register("products", ProductViewSet, basename="product")
router.register("orders", OrderViewSet, basename="order")
router.register("wishlist", WishlistViewSet, basename="wishlist")
router.register("reservations", ReservationViewSet, basename="reservation")

urlpatterns = [
    path("", include(router.urls)),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("guest-checkout/", GuestCheckoutView.as_view(), name="guest-checkout"),
    path("orders/me/", my_orders, name="my-orders"),
    path("payments/webhook/<str:provider>/", PaymentWebhookView.as_view(), name="payment-webhook"),
]
