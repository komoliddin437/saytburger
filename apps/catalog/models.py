from django.db import models

from apps.core.models import TimeStampedModel


class Category(TimeStampedModel):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Product(TimeStampedModel):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    search_document = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    @property
    def avg_rating(self):
        return self.ratings.filter(is_approved=True).aggregate(avg=models.Avg("rating")).get("avg")


class Ingredient(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    extra_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class ProductIngredient(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_ingredients")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT, related_name="product_ingredients")
    quantity_label = models.CharField(max_length=64, blank=True)
    is_optional = models.BooleanField(default=False)

    class Meta:
        unique_together = ("product", "ingredient")
        ordering = ["product", "ingredient__name"]

    def __str__(self) -> str:
        return f"{self.product.name} - {self.ingredient.name}"


class ProductRating(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="product_ratings")
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        unique_together = ("product", "user")
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(check=models.Q(rating__gte=1, rating__lte=5), name="product_rating_between_1_5"),
        ]

    def __str__(self) -> str:
        return f"{self.product.name} - {self.rating}"


class BranchProduct(TimeStampedModel):
    branch = models.ForeignKey("branches.Branch", on_delete=models.CASCADE, related_name="branch_products")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="branch_products")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ("branch", "product")
        indexes = [
            models.Index(fields=["branch", "is_available"]),
        ]

    def __str__(self) -> str:
        return f"{self.branch.name} - {self.product.name}"
