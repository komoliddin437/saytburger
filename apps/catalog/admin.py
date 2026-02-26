from django.contrib import admin

from .models import BranchProduct, Category, Ingredient, Product, ProductIngredient, ProductRating


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "base_price", "is_active", "created_at")
    list_filter = ("category", "is_active")
    search_fields = ("name",)


@admin.register(BranchProduct)
class BranchProductAdmin(admin.ModelAdmin):
    list_display = ("branch", "product", "price", "is_available")
    list_filter = ("branch", "is_available")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "extra_price", "is_active")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ProductIngredient)
class ProductIngredientAdmin(admin.ModelAdmin):
    list_display = ("product", "ingredient", "quantity_label", "is_optional")
    list_filter = ("is_optional",)
    search_fields = ("product__name", "ingredient__name")


@admin.register(ProductRating)
class ProductRatingAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "is_approved", "created_at")
    list_filter = ("rating", "is_approved")
    search_fields = ("product__name", "user__username", "comment")
