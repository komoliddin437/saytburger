from rest_framework import serializers

from apps.accounts.models import User, WishlistItem
from apps.branches.models import Branch, TableReservation
from apps.catalog.models import BranchProduct, Category, Product, ProductIngredient, ProductRating
from apps.orders.models import Order, OrderItem


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = (
            "id",
            "name",
            "slug",
            "address",
            "phone",
            "latitude",
            "longitude",
            "delivery_radius_km",
            "opens_at",
            "closes_at",
            "is_active",
        )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "is_active")


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    ingredients = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "description",
            "base_price",
            "image_url",
            "category",
            "category_name",
            "is_active",
            "ingredients",
            "avg_rating",
        )

    def get_ingredients(self, obj):
        rows = ProductIngredient.objects.filter(product=obj).select_related("ingredient")
        return [
            {
                "id": row.ingredient_id,
                "name": row.ingredient.name,
                "extra_price": row.ingredient.extra_price,
                "quantity_label": row.quantity_label,
                "is_optional": row.is_optional,
            }
            for row in rows
        ]

    def get_avg_rating(self, obj):
        return obj.avg_rating


class BranchProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = BranchProduct
        fields = ("id", "branch", "product", "price", "is_available")


class OrderItemWriteSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class OrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            "id",
            "branch",
            "status",
            "payment_status",
            "delivery_address",
            "delivery_lat",
            "delivery_lon",
            "scheduled_for",
            "promo_code",
            "bonus_points_used",
            "referral_code",
            "total_amount",
            "notes",
            "items",
            "created_at",
        )
        read_only_fields = ("status", "payment_status", "total_amount")

    def get_items(self, obj):
        return [
            {
                "id": item.id,
                "product_id": item.product_id,
                "product_name": item.product_name,
                "unit_price": item.unit_price,
                "quantity": item.quantity,
                "line_total": item.line_total,
            }
            for item in obj.items.all()
        ]


class OrderCreateSerializer(serializers.Serializer):
    branch = serializers.IntegerField()
    delivery_address = serializers.CharField(max_length=255)
    delivery_lat = serializers.FloatField(required=False)
    delivery_lon = serializers.FloatField(required=False)
    scheduled_for = serializers.DateTimeField(required=False)
    promo_code = serializers.CharField(max_length=64, required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    items = OrderItemWriteSerializer(many=True)

    def create(self, validated_data):
        request = self.context["request"]
        items_data = validated_data.pop("items")
        branch_id = validated_data.pop("branch")
        order = Order.objects.create(user=request.user, branch_id=branch_id, **validated_data)

        total = 0
        for row in items_data:
            product = Product.objects.get(pk=row["product_id"], is_active=True)
            branch_price = BranchProduct.objects.filter(branch_id=order.branch_id, product=product, is_available=True).first()
            unit_price = branch_price.price if branch_price else product.base_price
            item = OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                unit_price=unit_price,
                quantity=row["quantity"],
            )
            total += item.line_total

        order.total_amount = total
        order.save(update_fields=["total_amount", "updated_at"])
        return order


class ProductRatingSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = ProductRating
        fields = ("id", "product", "user", "username", "rating", "comment", "is_approved", "created_at")
        read_only_fields = ("user", "is_approved", "product")


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "phone",
            "bonus_points",
            "vip_status",
            "referral_code",
            "preferred_language",
            "two_factor_enabled",
            "preferred_branch",
        )
        read_only_fields = ("bonus_points", "vip_status", "referral_code")


class WishlistItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = WishlistItem
        fields = ("id", "product", "product_id", "created_at")

    def create(self, validated_data):
        user = self.context["request"].user
        product = Product.objects.get(pk=validated_data["product_id"], is_active=True)
        row, _ = WishlistItem.objects.get_or_create(user=user, product=product)
        return row


class GuestOrderCreateSerializer(OrderCreateSerializer):
    full_name = serializers.CharField(max_length=120)
    phone = serializers.CharField(max_length=32)

    def create(self, validated_data):
        full_name = validated_data.pop("full_name")
        phone = validated_data.pop("phone")
        request = self.context["request"]
        user = request.user if request.user.is_authenticated else None

        if user is None:
            digits = "".join(ch for ch in phone if ch.isdigit())[-10:] or "guest"
            username = f"guest_{digits}"
            email = f"{username}@guest.local"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"first_name": full_name[:120], "email": email, "phone": phone},
            )
            if created:
                user.set_unusable_password()
                user.save(update_fields=["password"])

        items_data = validated_data.pop("items")
        branch_id = validated_data.pop("branch")
        order = Order.objects.create(user=user, branch_id=branch_id, **validated_data)

        total = 0
        for row in items_data:
            product = Product.objects.get(pk=row["product_id"], is_active=True)
            branch_price = BranchProduct.objects.filter(branch_id=order.branch_id, product=product, is_available=True).first()
            unit_price = branch_price.price if branch_price else product.base_price
            item = OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                unit_price=unit_price,
                quantity=row["quantity"],
            )
            total += item.line_total

        order.total_amount = total
        order.save(update_fields=["total_amount", "updated_at"])
        return order


class TableReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TableReservation
        fields = ("id", "branch", "full_name", "phone", "guests_count", "reserved_for", "notes", "status", "created_at")
        read_only_fields = ("status",)
