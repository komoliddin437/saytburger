import json
from datetime import timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views.generic import TemplateView
from django.views.decorators.csrf import ensure_csrf_cookie

from apps.accounts.models import User
from apps.orders.models import Order


@method_decorator(ensure_csrf_cookie, name="dispatch")
class HomeView(TemplateView):
    template_name = "home.html"


@staff_member_required
def admin_dashboard(request):
    since = timezone.now() - timedelta(days=30)
    orders = Order.objects.filter(created_at__gte=since)

    daily = (
        orders.annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(total_sales=Sum("total_amount"), total_orders=Count("id"))
        .order_by("day")
    )
    labels = [row["day"].isoformat() for row in daily]
    sales = [float(row["total_sales"] or 0) for row in daily]
    counts = [int(row["total_orders"] or 0) for row in daily]
    context = {
        "orders_30d": orders.count(),
        "revenue_30d": float(orders.aggregate(total=Sum("total_amount")).get("total") or 0),
        "users_total": User.objects.count(),
        "chart_labels": json.dumps(labels),
        "chart_sales": json.dumps(sales),
        "chart_orders": json.dumps(counts),
        "recent_orders": Order.objects.select_related("user", "branch").order_by("-created_at")[:30],
    }
    return render(request, "admin/dashboard.html", context)
