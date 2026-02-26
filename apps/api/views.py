from django.core.cache import cache
from django.contrib.auth import get_user_model
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import connection
from django.db.models import Q

from apps.accounts.models import WishlistItem
from apps.branches.models import Branch, TableReservation
from apps.branches.services import get_nearest_branch
from apps.catalog.models import BranchProduct, Category, Product
from apps.orders.models import Order, OrderStatus
from apps.payments.models import PaymentProvider, PaymentTransaction
from apps.payments.services import mark_payment_success

from .serializers import (
    BranchProductSerializer,
    BranchSerializer,
    CategorySerializer,
    GuestOrderCreateSerializer,
    OrderCreateSerializer,
    OrderSerializer,
    ProductRatingSerializer,
    ProductSerializer,
    UserProfileSerializer,
    WishlistItemSerializer,
    TableReservationSerializer,
)


class BranchViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Branch.objects.filter(is_active=True)
    serializer_class = BranchSerializer
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        cache_key = "api:v1:branches:list"
        payload = self._cache_get(cache_key)
        if payload is None:
            payload = BranchSerializer(self.get_queryset(), many=True).data
            self._cache_set(cache_key, payload, timeout=60)
        return Response(payload)

    @staticmethod
    def _cache_get(key):
        try:
            return cache.get(key)
        except Exception:
            return None

    @staticmethod
    def _cache_set(key, value, timeout=60):
        try:
            cache.set(key, value, timeout=timeout)
        except Exception:
            return

    @action(detail=False, methods=["GET"], permission_classes=[permissions.AllowAny])
    def nearest(self, request):
        lat = request.query_params.get("lat")
        lon = request.query_params.get("lon")
        if lat is None or lon is None:
            return Response({"detail": "lat and lon are required"}, status=status.HTTP_400_BAD_REQUEST)

        nearest = get_nearest_branch(float(lat), float(lon))
        if not nearest:
            return Response({"detail": "No active branches found"}, status=status.HTTP_404_NOT_FOUND)

        branch, distance_km = nearest
        return Response(
            {
                "branch": BranchSerializer(branch).data,
                "distance_km": distance_km,
                "is_deliverable": branch.can_deliver(float(lat), float(lon)),
            }
        )


class ProductViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Product.objects.filter(is_active=True).select_related("category")
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = self.queryset
        query = self.request.query_params.get("q")
        category_id = self.request.query_params.get("category")
        if category_id:
            qs = qs.filter(category_id=category_id)
        if query:
            if connection.vendor == "postgresql":
                from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector

                vector = SearchVector("name", weight="A") + SearchVector("description", weight="B")
                search_query = SearchQuery(query)
                qs = (
                    qs.annotate(rank=SearchRank(vector, search_query))
                    .filter(rank__gte=0.05)
                    .order_by("-rank", "name")
                )
            else:
                qs = qs.filter(Q(name__icontains=query) | Q(description__icontains=query))
        return qs

    @action(detail=False, methods=["GET"], permission_classes=[permissions.AllowAny])
    def by_branch(self, request):
        branch_id = request.query_params.get("branch_id")
        if not branch_id:
            return Response({"detail": "branch_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        cache_key = f"api:v1:products:by_branch:{branch_id}"
        payload = self._cache_get(cache_key)
        if payload is not None:
            return Response(payload)
        qs = BranchProduct.objects.filter(branch_id=branch_id, is_available=True).select_related("product")
        payload = BranchProductSerializer(qs, many=True).data
        self._cache_set(cache_key, payload, timeout=60)
        return Response(payload)

    @staticmethod
    def _cache_get(key):
        try:
            return cache.get(key)
        except Exception:
            return None

    @staticmethod
    def _cache_set(key, value, timeout=60):
        try:
            cache.set(key, value, timeout=timeout)
        except Exception:
            return

    @action(detail=True, methods=["GET", "POST"], permission_classes=[permissions.AllowAny])
    def ratings(self, request, pk=None):
        product = self.get_object()
        if request.method == "GET":
            ratings = product.ratings.filter(is_approved=True).select_related("user")
            return Response(ProductRatingSerializer(ratings, many=True).data)

        serializer = ProductRatingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user if request.user.is_authenticated else self._get_or_create_guest_rater(request)
        row, _ = product.ratings.update_or_create(
            user=user,
            defaults={
                "rating": serializer.validated_data["rating"],
                "comment": serializer.validated_data.get("comment", ""),
            },
        )
        return Response(ProductRatingSerializer(row).data, status=status.HTTP_201_CREATED)

    @staticmethod
    def _get_or_create_guest_rater(request):
        User = get_user_model()
        ip = (request.META.get("HTTP_X_FORWARDED_FOR", "") or request.META.get("REMOTE_ADDR", "guest")).split(",")[0].strip()
        safe_ip = ip.replace(".", "_").replace(":", "_")
        username = f"guest_rater_{safe_ip}"[:150]
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": f"{username}@guest.local", "first_name": "Guest"},
        )
        if created:
            user.set_unusable_password()
            user.save(update_fields=["password"])
        return user


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")

    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["POST"])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status in {OrderStatus.DELIVERED, OrderStatus.CANCELLED}:
            return Response({"detail": "Order cannot be cancelled"}, status=status.HTTP_400_BAD_REQUEST)
        order.status = OrderStatus.CANCELLED
        order.save(update_fields=["status", "updated_at"])
        return Response(OrderSerializer(order).data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def my_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related("items")[:20]
    return Response(OrderSerializer(orders, many=True).data)


class PaymentWebhookView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, provider: str):
        if provider not in {PaymentProvider.CLICK, PaymentProvider.PAYME, PaymentProvider.STRIPE}:
            return Response({"detail": "Unsupported provider"}, status=status.HTTP_400_BAD_REQUEST)

        tx_id = request.data.get("transaction_id")
        if not tx_id:
            return Response({"detail": "transaction_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        transaction = PaymentTransaction.objects.filter(pk=tx_id, provider=provider).first()
        if not transaction:
            return Response({"detail": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)

        transaction.raw_payload = dict(request.data)
        transaction.save(update_fields=["raw_payload", "updated_at"])
        mark_payment_success(transaction)
        return Response({"ok": True})


class CategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = UserProfileSerializer(request.user).data
        profile["orders"] = OrderSerializer(
            Order.objects.filter(user=request.user).prefetch_related("items")[:20],
            many=True,
        ).data
        return Response(profile)

    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WishlistItem.objects.filter(user=self.request.user).select_related("product", "product__category")

    def perform_create(self, serializer):
        serializer.save()


class GuestCheckoutView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = GuestOrderCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class ReservationViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = TableReservationSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = TableReservation.objects.select_related("branch")
        phone = self.request.query_params.get("phone")
        if phone:
            qs = qs.filter(phone=phone)
        return qs[:50]
