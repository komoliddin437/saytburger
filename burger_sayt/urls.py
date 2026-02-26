from django.contrib import admin
from django.urls import include, path

from apps.core.views import HomeView, admin_dashboard

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("auth/", include("apps.accounts.urls")),
    path("admin/dashboard/", admin_dashboard, name="admin-dashboard"),
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.api.urls")),
    path("api/v2/", include("apps.api.v2_urls")),
]
