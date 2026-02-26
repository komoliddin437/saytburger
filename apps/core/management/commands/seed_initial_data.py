from datetime import time
from decimal import Decimal
from random import randint

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from apps.accounts.models import BranchMembership, BranchRole
from apps.branches.models import Branch, BranchSettings
from apps.catalog.models import BranchProduct, Category, Ingredient, Product, ProductIngredient


class Command(BaseCommand):
    help = "Seed initial enterprise data for Big Burger."

    @transaction.atomic
    def handle(self, *args, **options):
        self._seed_categories_products_ingredients()
        self._seed_branches()
        self._seed_branch_prices()
        self._seed_staff_users()
        self.stdout.write(self.style.SUCCESS("Initial data seeded successfully."))

    def _seed_categories_products_ingredients(self):
        categories = ["Signature Burgers", "Cheese Burgers", "Chicken Burgers", "Vegan Burgers", "Snacks", "Drinks", "Salads"]
        ingredients = [
            ("Beef Patty", "beef-patty", "12000"),
            ("Chicken Patty", "chicken-patty", "10000"),
            ("Cheddar", "cheddar", "5000"),
            ("Tomato", "tomato", "2000"),
            ("Onion", "onion", "1500"),
            ("Pickles", "pickles", "2000"),
            ("Lettuce", "lettuce", "1500"),
            ("Brioche Bun", "brioche-bun", "3500"),
            ("Vegan Patty", "vegan-patty", "11000"),
        ]
        product_rows = [
            ("Big Classic", "Signature Burgers", "45000", "https://images.unsplash.com/photo-1568901346375-23c9450c58cd"),
            ("Double Trouble", "Signature Burgers", "56000", "https://images.unsplash.com/photo-1550547660-d9450f859349"),
            ("Cheese Bomb", "Cheese Burgers", "49000", "https://images.unsplash.com/photo-1553979459-d2229ba7433b"),
            ("Chicken Crunch", "Chicken Burgers", "43000", "https://images.unsplash.com/photo-1550317138-10000687a72b"),
            ("Green Force", "Vegan Burgers", "47000", "https://images.unsplash.com/photo-1520072959219-c595dc870360"),
            ("Triple Smash", "Signature Burgers", "62000", "https://images.unsplash.com/photo-1594212699903-ec8a3eca50f5"),
            ("Bacon Melt", "Cheese Burgers", "54000", "https://images.unsplash.com/photo-1571091718767-18b5b1457add"),
            ("Spicy Chicken", "Chicken Burgers", "46000", "https://images.unsplash.com/photo-1561758033-7e924f619b47"),
            ("Crispy Vegan", "Vegan Burgers", "45000", "https://images.unsplash.com/photo-1606755962773-d324e0a13086"),
            ("French Fries", "Snacks", "18000", "https://images.unsplash.com/photo-1576107232684-1279f390859f"),
            ("Curly Fries", "Snacks", "21000", "https://images.unsplash.com/photo-1639024471283-03518883512d"),
            ("Cheese Fries", "Snacks", "24000", "https://images.unsplash.com/photo-1541592106381-b31e9677c0e5"),
            ("Onion Rings", "Snacks", "22000", "https://images.unsplash.com/photo-1639744210965-33a57d6f560d"),
            ("Nuggets 6pcs", "Snacks", "27000", "https://images.unsplash.com/photo-1562967914-608f82629710"),
            ("Coca-Cola 0.5", "Drinks", "12000", "https://images.unsplash.com/photo-1554866585-cd94860890b7"),
            ("Fanta 0.5", "Drinks", "12000", "https://images.unsplash.com/photo-1624517452488-04869289c4ca"),
            ("Sprite 0.5", "Drinks", "12000", "https://images.unsplash.com/photo-1581006852262-e4307cf6283a"),
            ("Mineral Water", "Drinks", "6000", "https://images.unsplash.com/photo-1523362628745-0c100150b504"),
            ("Ice Tea Lemon", "Drinks", "14000", "https://images.unsplash.com/photo-1556679343-c7306c1976bc"),
            ("Caesar Salad", "Salads", "32000", "https://images.unsplash.com/photo-1512852939750-1305098529bf"),
            ("Greek Salad", "Salads", "30000", "https://images.unsplash.com/photo-1546793665-c74683f339c1"),
            ("Garden Salad", "Salads", "27000", "https://images.unsplash.com/photo-1512621776951-a57141f2eefd"),
        ]

        category_map = {}
        for name in categories:
            category_map[name], _ = Category.objects.get_or_create(
                slug=slugify(name),
                defaults={"name": name, "is_active": True},
            )

        ingredient_map = {}
        for name, slug, extra_price in ingredients:
            ingredient_map[name], _ = Ingredient.objects.get_or_create(
                slug=slug,
                defaults={"name": name, "extra_price": Decimal(extra_price), "is_active": True},
            )

        for product_name, category_name, base_price, image_url in product_rows:
            product, _ = Product.objects.get_or_create(
                name=product_name,
                defaults={
                    "category": category_map[category_name],
                    "description": f"{product_name} crafted for enterprise menu.",
                    "base_price": Decimal(base_price),
                    "image_url": image_url,
                    "is_active": True,
                    "search_document": f"{product_name} {category_name} burger",
                },
            )
            for ingredient_name in ("Brioche Bun", "Tomato", "Onion", "Lettuce"):
                ProductIngredient.objects.get_or_create(
                    product=product,
                    ingredient=ingredient_map[ingredient_name],
                    defaults={"quantity_label": "1x", "is_optional": ingredient_name in {"Onion"}},
                )

    def _seed_branches(self):
        branch_rows = [
            ("Big Burger Tashkent Center", "Amir Temur ko'chasi 10", "+998901112233", 41.311081, 69.240562),
            ("Big Burger Chilonzor", "Chilonzor 19-kvartal", "+998901112244", 41.275736, 69.204746),
            ("Big Burger Yunusobod", "Yunusobod 7-mavze", "+998901112255", 41.366842, 69.288145),
        ]
        for name, address, phone, lat, lon in branch_rows:
            branch, _ = Branch.objects.get_or_create(
                slug=slugify(name),
                defaults={
                    "name": name,
                    "address": address,
                    "phone": phone,
                    "latitude": lat,
                    "longitude": lon,
                    "delivery_radius_km": 7.0,
                    "opens_at": time(hour=9),
                    "closes_at": time(hour=23),
                    "is_active": True,
                },
            )
            BranchSettings.objects.get_or_create(
                branch=branch,
                defaults={
                    "min_order_amount": Decimal("25000"),
                    "service_fee": Decimal("5000"),
                    "tax_percent": Decimal("12.0"),
                    "is_accepting_orders": True,
                },
            )

    def _seed_branch_prices(self):
        branches = list(Branch.objects.filter(is_active=True))
        products = list(Product.objects.filter(is_active=True))
        for branch in branches:
            for product in products:
                multiplier = Decimal(100 + randint(-5, 8)) / Decimal(100)
                price = (product.base_price * multiplier).quantize(Decimal("1.00"))
                BranchProduct.objects.get_or_create(
                    branch=branch,
                    product=product,
                    defaults={"price": price, "is_available": True},
                )

    def _seed_staff_users(self):
        User = get_user_model()
        staff_rows = [
            ("chef", "chef@bigburger.local", BranchRole.CHEF),
            ("courier", "courier@bigburger.local", BranchRole.COURIER),
            ("manager", "manager@bigburger.local", BranchRole.MANAGER),
        ]
        branch = Branch.objects.filter(is_active=True).first()
        if not branch:
            return
        for username, email, role in staff_rows:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "is_staff": True,
                    "phone": "+998900000000",
                },
            )
            if created:
                user.set_password("ChangeMe123!")
                user.save(update_fields=["password"])
            BranchMembership.objects.get_or_create(
                user=user,
                branch=branch,
                role=role,
                defaults={"is_active": True},
            )
