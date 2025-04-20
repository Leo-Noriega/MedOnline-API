from django.urls import path, include
from .views import *

urlpatterns = [
    path('mis-citas/', my_appointments, name='mis-citas-paciente'),
    path('mi-cuenta/', my_account_user, name='mi-account-user'),
]