from django.db.models import Avg, OuterRef, Subquery
from rest_framework import mixins, permissions, viewsets

from apps.catalog.models import BranchProduct, Product

from .serializers import ProductSerializer
from .views import BranchViewSet, OrderViewSet, PaymentWebhookView


class ProductV2ViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        branch_id = self.request.query_params.get("branch_id")
        qs = Product.objects.filter(is_active=True).select_related("category")
        if branch_id:
            branch_price_sq = BranchProduct.objects.filter(
                branch_id=branch_id,
                product_id=OuterRef("pk"),
                is_available=True,
            ).values("price")[:1]
            qs = qs.annotate(branch_price=Subquery(branch_price_sq))
        return qs.annotate(avg_rating_score=Avg("ratings__rating"))


__all__ = [
    "BranchViewSet",
    "OrderViewSet",
    "PaymentWebhookView",
    "ProductV2ViewSet",
]
