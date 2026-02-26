from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import AppLoginForm, AppRegisterForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = AppLoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        messages.success(request, "Muvaffaqiyatli kirdingiz.")
        return redirect("home")
    return render(request, "auth/login.html", {"form": form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = AppRegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Akkaunt yaratildi.")
        return redirect("home")
    return render(request, "auth/register.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Hisobdan chiqdingiz.")
    return redirect("home")
