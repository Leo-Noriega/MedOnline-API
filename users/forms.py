from django import forms

from django.contrib.auth.forms import AuthenticationForm

INPUT_CLASS = 'form-control'


class CustomLoginForm(AuthenticationForm):
    email = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.TextInput(attrs={'class': INPUT_CLASS})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': INPUT_CLASS})
    )
