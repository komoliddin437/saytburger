from django.urls import path

from .views import login_view, logout_view, register_view

urlpatterns = [
    path("login/", login_view, name="app-login"),
    path("register/", register_view, name="app-register"),
    path("logout/", logout_view, name="app-logout"),
]
