from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


class AppLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Username"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Parol"}))


class AppRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"placeholder": "Email"}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={"placeholder": "Telefon"}))

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "phone", "password1", "password2")
